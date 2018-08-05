# cinder_volume_delete

```
usage: delete_volume.py [-h] CINDER_VOLUME_UUID

This script will remove "stuck" cinder volumes. By stuck, that means they may
be stuck in detaching, deleting, etc. This script will remove the attachment
and the volume in the database!

positional arguments:
  CINDER_VOLUME_UUID  The UUID of the Cinder volume that needs to be removed

optional arguments:
  -h, --help          show this help message and exit
```

### Host Requirements

Because of the usage of `MySQLdb`, this requires `libmysqlclient-dev` installed on the host in order to build the module.

```
sudo apt-get install -y libmysqlclient-dev
```

### Installing Python Requirements

Install recommended in a virtualenv

```
pip install -r requirements.txt
```
