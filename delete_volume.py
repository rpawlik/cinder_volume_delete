#!/bin/env python

import sys
import MySQLdb
import argparse
import ConfigParser

parser = argparse.ArgumentParser(description='This script will remove "stuck" cinder volumes. By stuck, that means they may be stuck in detaching, deleting, etc. This script will remove the attachment and the volume in the database!')
parser.add_argument('volume_uuid', metavar='CINDER_VOLUME_UUID',
                    help='The UUID of the Cinder volume that needs to be removed')
args = parser.parse_args()
vol_uuid = args.volume_uuid

# Get connection info from /root/.my.cnf

sql_ini_fileparser = ConfigParser.RawConfigParser()
sql_ini_fileparser.read('/root/.my.cnf')
host = sql_ini_fileparser.get('client', 'host')
user = sql_ini_fileparser.get('client', 'user')
password = sql_ini_fileparser.get('client', 'password')

# Connect to MySQL and get cursor
db = MySQLdb.connect(host=host, user=user, passwd=password)
cursor = db.cursor()

# DB queries
query1 = "UPDATE cinder.volumes SET attach_status='detached',deleted_at=NOW(),deleted=1,status='deleted',attach_status='detached',terminated_at=NOW() WHERE id='{}'".format(vol_uuid)
query2 = "UPDATE cinder.volume_attachment SET attach_status='detached', deleted=1, detach_time=NOW(), deleted_at=NOW() WHERE volume_id='{}'".format(vol_uuid)
query3 = "UPDATE cinder.volume_admin_metadata SET deleted=1, updated_at=NOW(), deleted_at=NOW() WHERE volume_id='{}' AND deleted=0".format(vol_uuid)
query4 = "UPDATE nova.block_device_mapping SET deleted=1, deleted_at=NOW() WHERE volume_id='{}'".format(vol_uuid)

# Ramsey: TODO - turn this into one function or just a for loop to interrate through the queries

# Run DB queries
try:
    cursor.execute(query1)
    db.commit()
except:
    db.rollback()

try:
    cursor.execute(query2)
    db.commit()
except:
    db.rollback()

try:
    cursor.execute(query3)
    db.commit()
except:
    db.rollback()

try:
    cursor.execute(query4)
    db.commit()
except:
    db.rollback()

print('{} has been cleaned up in the database. Please verify the volume has been removed on the cinder backend.'.format(vol_uuid))

# Get backend details
cursor.execute("""SELECT host from cinder.volumes WHERE id='{}'""".format(vol_uuid))

backends = cursor.fetchone()
for backend in backends:
    print('Backend Host: {}'.format(backend))

db.close()
