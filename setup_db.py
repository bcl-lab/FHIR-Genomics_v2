'''
Script to prepare a local postgresql instance for the server,
for more advanced usage, well, this won't help 
'''
import os
import subprocess
from config import PGUSERNAME, PGPASSWORD, DBNAME

if __name__ == '__main__':
    os.environ['PGPASSWORD'] = PGPASSWORD
    cmd = 'psql -U %s -c "CREATE DATABASE %s"'% (PGUSERNAME, DBNAME)
    print cmd
    subprocess.call(cmd, shell=True)
