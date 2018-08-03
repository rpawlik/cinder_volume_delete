# cinder_volume_delete

usage: delete_volume.py [-h] CINDER_VOLUME_UUID

This script will remove "stuck" cinder volumes. By stuck, that means they may
be stuck in detaching, deleting, etc. This script will remove the attachment
and the volume in the database!

positional arguments:
  CINDER_VOLUME_UUID  The UUID of the Cinder volume that needs to be removed

optional arguments:
  -h, --help          show this help message and exit
