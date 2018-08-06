#!/usr/bin/env python2

import sys
import argparse
import ConfigParser
import MySQLdb


def main():
    desc = (
        "This script will remove \"stuck\" cinder volumes. "
        "By stuck, that means they may be stuck in detaching, "
        "deleting, etc. This script will remove the attachment "
        "and the volume in the database! ")
    help_text = "The UUID of the Cinder volume that needs to be removed"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('volume_uuid', metavar='CINDER_VOLUME_UUID',
                        help=help_text)
    parser.add_argument('--delete', action='store_const', const=True,
                        default=False, dest='delete',
                        help='Mark this volume as deleted.')
    args = parser.parse_args()
    vol_uuid = args.volume_uuid
    delete = args.delete

    # Get connection info from /root/.my.cnf

    sql_ini_fileparser = ConfigParser.RawConfigParser()
    sql_ini_fileparser.read('/root/.my.cnf')
    host = sql_ini_fileparser.get('client', 'host')
    user = sql_ini_fileparser.get('client', 'user')
    password = sql_ini_fileparser.get('client', 'password')

    queries = {
        "cinder": [],
        "nova": []
        }

    queries["cinder"].append("""
        UPDATE cinder.volume_attachment
        SET attach_status='detached',
            deleted=1,
            detach_time=NOW(),
            deleted_at=NOW()
        WHERE deleted=0
          AND volume_id='{}'""".format(vol_uuid))
    queries["nova"].append("""
        UPDATE nova.block_device_mapping
        SET deleted=id,
            deleted_at=NOW()
        WHERE deleted=0
          AND volume_id='{}'""".format(vol_uuid))

    if delete:
        queries["cinder"].append("""
            UPDATE cinder.volumes
            SET attach_status='detached',
                deleted_at=NOW(),
                deleted=1,
                status='deleted',
                terminated_at=NOW()
            WHERE deleted=0
              AND id='{}'""".format(vol_uuid))
        queries["cinder"].append("""
            UPDATE cinder.volume_admin_metadata
            SET deleted=1,
                updated_at=NOW(),
                deleted_at=NOW()
            WHERE deleted=0
              AND volume_id='{}'""".format(vol_uuid))

    else:
        queries["cinder"].append("""
            UPDATE cinder.volumes
            SET attach_status='detached',
                status='available',
            WHERE deleted=0
              AND id='{}'""".format(vol_uuid))

    for db_name, db_queries in queries.iteritems():
        db = MySQLdb.connect(host=host, user=user, passwd=password, db=db_name)
        db.autocommit(False)
        cursor = db.cursor()

        try:
            for query in db_queries:
                cursor.execute(query)
                print "Updating {} row(s) on {}".format(
                    db.affected_rows(), query.split()[1])
        except Exception as e:
            print e
            print "Something broke while executing ({}) {}".format(
                db_name, query)
            db.rollback()
            break

        if yes_no("Commit changes to {} (y/n)? ".format(db_name)):
            db.commit()
        else:
            break

        db.close()


def yes_no(answer):
    yes = set(['yes', 'y'])
    no = set(['no', 'n', ''])

    while True:
        choice = raw_input(answer).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print "Please respond with 'yes' or 'no'\n"


if __name__ == '__main__':
    sys.exit(main())
