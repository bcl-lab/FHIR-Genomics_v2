import subprocess
import sys
import os
from multiprocessing import cpu_count
from argparse import ArgumentParser
from fhir import create_app, db
from config import APP_CONFIG, HOST
# use this for WSGI server
# e.g. `$ gunicorn server:app`
app = create_app(APP_CONFIG)


def clear_db(app):
    '''
    Wipes the database associated with the app.
    '''
    with app.app_context():
        db.drop_all()
        db.create_all() 

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('option', nargs='?', default='run', choices=('run', 'clear'))
    arg_parser.add_argument('-d', '--debug', action='store_true')
    args = arg_parser.parse_args()
    if args.option == 'run':
        if args.debug == True:
            #app.run(debug=True)
            app.run(port=2048, debug=True)
        else:
            num_workers = cpu_count() * 2 + 1
            cmd = 'gunicorn -w %d -b %s -D server:app --log-level error --log-file fhir.log'% (num_workers, HOST)
            subprocess.call(cmd, shell=True)
    elif args.option == 'clear':
        clear_db(app)
