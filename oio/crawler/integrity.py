from __future__ import print_function
import os
import csv
import sys
import cStringIO
from itertools import chain
import argparse

from eventlet.event import Event
from eventlet.greenpool import GreenPool

from oio.common import exceptions as exc
from oio.account.client import AccountClient
from oio.container.client import ContainerClient
from oio.blob.client import BlobClient


class Target(object):
    def __init__(self, account, container=None, obj=None, chunk=None):
        self.account = account
        self.container = container
        self.obj = obj
        self.chunk = chunk

    def copy(self):
        return Target(
            self.account,
            self.container,
            self.obj,
            self.chunk)

    def __repr__(self):
        s = "account=" + self.account
        if self.container:
            s += ', container=' + self.container
        if self.obj:
            s += ', obj=' + self.obj
        if self.chunk:
            s += ', chunk=' + self.chunk
        return s


class Checker(object):
    def __init__(self, namespace, concurrency=50, error_file=None):
        self.pool = GreenPool(concurrency)
        self.error_file = error_file
        if self.error_file:
            f = open(self.error_file, 'a')
            self.error_writer = csv.writer(f, delimiter=' ')

        conf = {'namespace': namespace}
        self.account_client = AccountClient(conf)
        self.container_client = ContainerClient(conf)
        self.blob_client = BlobClient()

        self.accounts_checked = 0
        self.containers_checked = 0
        self.objects_checked = 0
        self.chunks_checked = 0
        self.account_not_found = 0
        self.container_not_found = 0
        self.object_not_found = 0
        self.chunk_not_found = 0
        self.account_exceptions = 0
        self.container_exceptions = 0
        self.object_exceptions = 0
        self.chunk_exceptions = 0

        self.list_cache = {}
        self.running = {}

    def write_error(self, target):
        error = [target.account]
        if target.container:
            error.append(target.container)
        if target.obj:
            error.append(target.obj)
        if target.chunk:
            error.append(target.chunk)
        self.error_writer.writerow(error)

    def check_chunk(self, target):
        account = target.account
        container = target.container
        obj = target.obj
        chunk = target.chunk

        obj_listing = self.check_obj(target)
        error = False
        if chunk not in obj_listing:
            print('  Chunk %s missing in object listing' % target)
            error = True
            checksum = None
        else:
            checksum = obj_listing[chunk]['hash']

        resp = None
        try:
            resp = self.blob_client.chunk_head(chunk)
        except exc.NotFound as e:
            self.chunk_not_found += 1
            error = True
            print('  Not found chunk "%s": %s' % (target, str(e)))
        except Exception as e:
            self.chunk_exceptions += 1
            error = True
            print('  Exception chunk "%s": %s' % (target, str(e)))

        # TODO check checksum match

        if error and self.error_file:
            self.write_error(target)
        self.chunks_checked += 1

    def check_obj(self, target, recurse=False):
        account = target.account
        container = target.container
        obj = target.obj

        if (account, container, obj) in self.running:
            self.running[(account, container, obj)].wait()
        if (account, container, obj) in self.list_cache:
            return self.list_cache[(account, container, obj)]
        self.running[(account, container, obj)] = Event()
        print('Checking object "%s"' % target)
        container_listing = self.check_container(target)
        error = False
        if obj not in container_listing:
            print('  Object %s missing in container listing' % target)
            error = True
            checksum = None
        else:
            checksum = container_listing[obj]['hash']

        results = []
        try:
            _, resp = self.container_client.content_show(
                    acct=account, ref=container,path=obj)
        except exc.NotFound as e:
            self.object_not_found += 1
            error = True
            print('  Not found object "%s": %s' % (target, str(e)))
        except Exception as e:
            self.object_exceptions += 1
            error = True
            print(' Exception object "%s": %s' % (target, str(e)))
        else:
            results = resp

        chunk_listing = dict()
        for chunk in results:
            chunk_listing[chunk['url']] = chunk

        self.objects_checked += 1
        self.list_cache[(account, container, obj)] = chunk_listing
        self.running[(account, container, obj)].send(True)
        del self.running[(account, container, obj)]

        if recurse:
            for chunk in chunk_listing:
                t = target.copy()
                t.chunk = chunk
                self.pool.spawn_n(self.check_chunk, t)
        if error and self.error_file:
            self.write_error(target)
        return chunk_listing

    def check_container(self, target, recurse=False):
        account = target.account
        container = target.container

        if (account, container) in self.running:
            self.running[(account, container)].wait()
        if (account, container) in self.list_cache:
            return self.list_cache[(account, container)]
        self.running[(account, container)] = Event()
        print('Checking container "%s"' % target)
        account_listing = self.check_account(target)
        error = False
        if container not in account_listing:
            error = True
            print('  Container %s missing in account listing' % target)

        marker = None
        results = []
        while True:
            try:
                resp = self.container_client.container_list(
                    acct=account, ref=container, marker=marker)
            except exc.NotFound as e:
                self.container_not_found += 1
                error = True
                print('  Not found container "%s": %s' % (target, str(e)))
                break
            except Exception as e:
                self.container_exceptions += 1
                error = True
                print('  Exception container "%s": %s' % (target, str(e)))
                break

            if resp['objects']:
                marker = resp['objects'][-1]['name']
            else:
                break
            results.extend(resp['objects'])

        container_listing = dict()
        for obj in results:
            container_listing[obj['name']] = obj

        self.containers_checked += 1
        self.list_cache[(account, container)] = container_listing
        self.running[(account, container)].send(True)
        del self.running[(account, container)]

        if recurse:
            for obj in container_listing:
                t = target.copy()
                t.obj = obj
                self.pool.spawn_n(self.check_obj, t, True)
        if error and self.error_file:
            self.write_error(target)
        return container_listing

    def check_account(self, target, recurse=False):
        account = target.account

        if account in self.running:
            self.running[account].wait()
        if account in self.list_cache:
            return self.list_cache[account]
        self.running[account] = Event()
        print('Checking account "%s"' % target)
        error = False
        marker = None
        results = []
        while True:
            try:
                resp = self.account_client.containers_list(account, marker=marker)
            except Exception as e:
                self.account_exceptions += 1
                error = True
                print('  Exception account "%s": %s' % (target, str(e)))
                break
            if resp['listing']:
                marker = resp['listing'][-1][0]
            else:
                break
            results.extend(resp['listing'])

        containers = dict()
        for e in results:
            containers[e[0]] = (e[1], e[2])

        self.list_cache[account] = containers
        self.running[account].send(True)
        del self.running[account]
        self.accounts_checked += 1

        if recurse:
            for container in containers:
                t = target.copy()
                t.container = container
                self.pool.spawn_n(self.check_container, t, True)

        if error and self.error_file:
            self.write_error(target)
        return containers

    def check(self, target):
        if target.chunk and target.obj and target.container:
            self.pool.spawn_n(self.check_chunk, target)
        elif target.obj and target.container:
            self.pool.spawn_n(self.check_obj, target, True)
        elif target.container:
            self.pool.spawn_n(self.check_container, target, True)
        else:
            self.pool.spawn_n(self.check_account, target, True)

    def wait(self):
        self.pool.waitall()

    def report(self):
        def _report_stat(name, stat):
            print("{0:18}: {1}".format(name, stat))

        print()
        print('Report')
        _report_stat("Accounts checked", self.accounts_checked)
        if self.account_not_found:
            _report_stat("Missing accounts", self.account_not_found)
        if self.account_exceptions:
            _report_stat("Exceptions", self.account_not_found)
        print()
        _report_stat("Containers checked", self.containers_checked)
        if self.container_not_found:
            _report_stat("Missing containers", self.container_not_found)
        if self.container_exceptions:
            _report_stat("Exceptions", self.container_exceptions)
        print()
        _report_stat("Objects checked", self.objects_checked)
        if self.object_not_found:
            _report_stat("Missing objects", self.object_not_found)
        if self.object_exceptions:
            _report_stat("Exceptions", self.object_exceptions)
        print()
        _report_stat("Chunks checked", self.chunks_checked)
        if self.chunk_not_found:
            _report_stat("Missing chunks", self.chunk_not_found)
        if self.chunk_exceptions:
            _report_stat("Exceptions", self.chunk_exceptions)


def main():
    parser = argparse.ArgumentParser(description="Check integrity")
    parser.add_argument('namespace', help='namespace name')
    parser.add_argument('target', metavar='T', nargs='*',
                        help='target to check integrity')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('-v', '--verbose',
                      action='store_true', help='verbose output')

    args = parser.parse_args()

    checker = Checker(args.namespace, error_file=args.output)
    if not os.isatty(sys.stdin.fileno()):
        source = sys.stdin
    else:
        source = cStringIO.StringIO(' '.join(args.target))
    args = csv.reader(source, delimiter=' ')
    for entry in args:
        checker.check(Target(*entry))
    checker.wait()
    checker.report()
