# Copyright (C) 2015-2018 OpenIO SAS, as part of OpenIO SDS
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

HEADER_PREFIX = 'x-oio-'
ADMIN_HEADER = HEADER_PREFIX + 'admin'
CHECKHASH_HEADER = HEADER_PREFIX + 'check-hash'
FETCHXATTR_HEADER = HEADER_PREFIX + 'xattr'
FORCEMASTER_HEADER = HEADER_PREFIX + 'force-master'
FORCEVERSIONING_HEADER = HEADER_PREFIX + 'force-versioning'
PERFDATA_HEADER = HEADER_PREFIX + 'perfdata'
PERFDATA_HEADER_PREFIX = PERFDATA_HEADER + '-'
REQID_HEADER = HEADER_PREFIX + 'req-id'

CONTAINER_METADATA_PREFIX = "x-oio-container-meta-"
OBJECT_METADATA_PREFIX = "x-oio-content-meta-"
CHUNK_METADATA_PREFIX = "x-oio-chunk-meta-"

CONTAINER_USER_METADATA_PREFIX = CONTAINER_METADATA_PREFIX + 'user-'

TIMEOUT_HEADER = HEADER_PREFIX + 'timeout'

CONNECTION_TIMEOUT = 2.0
READ_TIMEOUT = 30.0

STRLEN_REFERENCEID = 66
STRLEN_CHUNKID = 64
STRLEN_REQID = 63

# Version of the format of chunk extended attributes
OIO_VERSION = '4.2'

OIO_DB_ENABLED = 0
OIO_DB_FROZEN = 2 ** 32 - 1
OIO_DB_DISABLED = 2 ** 32 - 2

OIO_DB_STATUS_NAME = {
    OIO_DB_ENABLED: "Enabled",
    OIO_DB_FROZEN: "Frozen",
    OIO_DB_DISABLED: "Disabled",
    str(OIO_DB_ENABLED): "Enabled",
    str(OIO_DB_FROZEN): "Frozen",
    str(OIO_DB_DISABLED): "Disabled",
}

CONTAINER_HEADERS = {
    "size": "%ssys-m2-usage" % CONTAINER_METADATA_PREFIX,
    "ns": "%ssys-ns" % CONTAINER_METADATA_PREFIX
}

OBJECT_HEADERS = {
    "name": "%sname" % OBJECT_METADATA_PREFIX,
    "id": "%sid" % OBJECT_METADATA_PREFIX,
    "policy": "%spolicy" % OBJECT_METADATA_PREFIX,
    "version": "%sversion" % OBJECT_METADATA_PREFIX,
    "size": "%slength" % OBJECT_METADATA_PREFIX,
    "ctime": "%sctime" % OBJECT_METADATA_PREFIX,
    "hash": "%shash" % OBJECT_METADATA_PREFIX,
    "mime_type": "%smime-type" % OBJECT_METADATA_PREFIX,
    "chunk_method": "%schunk-method" % OBJECT_METADATA_PREFIX
}

CHUNK_HEADERS = {
    "container_id": "%scontainer-id" % CHUNK_METADATA_PREFIX,
    "chunk_id": "%schunk-id" % CHUNK_METADATA_PREFIX,
    "chunk_hash": "%schunk-hash" % CHUNK_METADATA_PREFIX,
    "chunk_size": "%schunk-size" % CHUNK_METADATA_PREFIX,
    "chunk_pos": "%schunk-pos" % CHUNK_METADATA_PREFIX,
    "content_id": "%scontent-id" % CHUNK_METADATA_PREFIX,
    "content_chunkmethod": "%scontent-chunk-method" % CHUNK_METADATA_PREFIX,
    "content_policy": "%scontent-storage-policy" % CHUNK_METADATA_PREFIX,
    "content_path": "%scontent-path" % CHUNK_METADATA_PREFIX,
    "content_version": "%scontent-version" % CHUNK_METADATA_PREFIX,
    "metachunk_size": "%smetachunk-size" % CHUNK_METADATA_PREFIX,
    "metachunk_hash": "%smetachunk-hash" % CHUNK_METADATA_PREFIX,
    "full_path": "%sfull-path" % CHUNK_METADATA_PREFIX,
    "oio_version": "%soio-version" % CHUNK_METADATA_PREFIX,
}

CHUNK_XATTR_KEYS = {
    'chunk_hash': 'grid.chunk.hash',
    'chunk_id': 'grid.chunk.id',
    'chunk_pos': 'grid.chunk.position',
    'chunk_size': 'grid.chunk.size',
    'content_chunkmethod': 'grid.content.chunk_method',
    'container_id': 'grid.content.container',
    'content_id': 'grid.content.id',
    'content_path': 'grid.content.path',
    'content_policy': 'grid.content.storage_policy',
    'content_version': 'grid.content.version',
    'metachunk_hash': 'grid.metachunk.hash',
    'metachunk_size': 'grid.metachunk.size',
    'oio_version': 'grid.oio.version'
}

CHUNK_XATTR_CONTENT_FULLPATH_PREFIX = 'oio.content.fullpath:'

CHUNK_XATTR_KEYS_OPTIONAL = {
        'content_chunksnb': True,
        'chunk_hash': True,
        'chunk_size': True,
        'metachunk_size': True,
        'metachunk_hash': True,
        'oio_version': True,
        # Superseded by full_path
        'container_id': True,
        'content_id': True,
        'content_path': True,
        'content_version': True,
}

VOLUME_XATTR_KEYS = {
    'namespace': 'server.ns',
    'type': 'server.type',
    'id': 'server.id'}

# TODO(FVE): remove from versions 5.1+
chunk_xattr_keys = CHUNK_XATTR_KEYS
chunk_xattr_keys_optional = CHUNK_XATTR_KEYS_OPTIONAL
container_headers = CONTAINER_HEADERS
object_headers = OBJECT_HEADERS
volume_xattr_keys = VOLUME_XATTR_KEYS

# Suffix of chunk file names that have been declared corrupt
CHUNK_SUFFIX_CORRUPT = '.corrupt'
# Suffix of chunk file names that are not finished being uploaded
CHUNK_SUFFIX_PENDING = '.pending'
