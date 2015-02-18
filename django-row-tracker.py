import argparse
import sys
import os

#import myzodb
#from django.core.management import setup_environ
#
#import settings
#setup_environ(settings)

def get_model_info():
    '''
    Dump all models and their row counts to the screen
    '''
    from django.conf import settings
    from django.db.utils import DatabaseError
    from django.db.transaction import rollback_unless_managed
    from django.db import models

    project_models = models.get_models(include_auto_created=True)

    for them in project_models:
        try:
            print them._meta.db_table + " " + str(them.objects.all().count())
        except DatabaseError:
            print "Unexpected error and continuing:", sys.exc_info()[0] , " ", them
            rollback_unless_managed()
        except:
            print "Unexpected error and abending:", sys.exc_info()[0]
            break

def process_args():
    '''
    Process command line args
    '''
    parser = argparse.ArgumentParser("Obtains and records the number of rows in a tables of a Django Project at run time")
    parser.add_argument('--version', action='version', version='%(prog)s - Release : 1.0')
    parser.add_argument("path_to_project_root", help="Path to the root of the Django project of interest (that is the directory below 'manage.py')")
    parser.add_argument("project_name", help='''The name of the Django project of interest''')
    args = parser.parse_args()

    return args

def setup_env(args):
    '''
    Do what's necessary to allow this script to access the
    ORM of the Django project specified on the command line
    '''
    sys.path.append(os.path.abspath(args.path_to_project_root))
    sys.path.append('%s/%s' % (os.path.abspath(args.path_to_project_root), args.project_name))
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % args.project_name

def main():
    '''
    Handle main processing
    '''
    args = process_args()
    setup_env(args)
    get_model_info()


if __name__ == "__main__":
    main()

