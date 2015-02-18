import argparse
import sys
import os
import datetime

#import myzodb
#from django.core.management import setup_environ
#
#import settings
#setup_environ(settings)

import sqlite3

def create_tables_if_necessary(conn):
    lst_sql = []
    lst_sql.append('''
    CREATE TABLE IF NOT EXISTS [DRC_PROJECT] (  \
            [PRO_ID] INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,  \
            [PRO_NAME] NVARCHAR(128)  UNIQUE NULL  \
            );  \
    ''')

    lst_sql.append('''  \
    CREATE TABLE IF NOT EXISTS [DRC_MODEL] (  \
            [MOD_ID] INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,  \
            [MOD_PRO_ID] INTEGER  NULL,  \
            [MOD_TABLENAME] NVARCHAR(256) NOT NULL  \
            );  \
    ''')

    lst_sql.append('''
    CREATE TABLE IF NOT EXISTS [DRC_RUN] (  \
            [RUN_ID] INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,  \
            [RUN_PRO_ID] INTEGER  NULL,  \
            [RUN_TIME] TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,  \
            [RUN_COMMENT] NVARCHAR(256)  UNIQUE NULL  \
            );  \
    ''')

    lst_sql.append('''
    CREATE TABLE IF NOT EXISTS [DRC_RUN_RESULTS] (  \
            [RUR_ID] INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,  \
            [RUR_RUN_ID] INTEGER  NULL,  \
            [RUR_MOD_ID] INTEGER  NULL,  \
            [RUR_ROW_COUNT] INTEGER  NULL  \
            );  \
    ''')

    for sql in lst_sql:
        conn.execute(sql)

    conn.commit()

def initialize_for_this_run(conn, project_name):

    c = conn.cursor()

    #Get or create Project
    c.execute('''SELECT * FROM DRC_PROJECT WHERE PRO_NAME = "{proj_name}"'''.format(proj_name=project_name))
    id_exists = c.fetchone()
    if id_exists:
        proj_id = id_exists[0]
    else:
        c.execute('''INSERT INTO DRC_PROJECT (PRO_NAME) VALUES ("{proj_name}")'''.format(proj_name=project_name))
        proj_id = c.lastrowid

    #Create a Run row
    comment = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    c.execute('''INSERT INTO DRC_RUN (RUN_PRO_ID, RUN_COMMENT) VALUES ({pro_id}, "{the_comment}")'''.format(pro_id=proj_id, the_comment=comment))
    run_id = c.lastrowid

    conn.commit()

    return {'proj_id':proj_id, 'run_id':run_id}

def insert_run_result(conn, proj_id, run_id, tab_name, row_count):

    c = conn.cursor()
    #Get or create Project
    c.execute('''SELECT * FROM DRC_MODEL WHERE MOD_PRO_ID = {proj_id} AND MOD_TABLENAME = "{table_name}"'''.format(proj_id=proj_id, table_name=tab_name))
    id_exists = c.fetchone()
    if id_exists:
        mod_id = id_exists[0]
    else:
        c.execute('''INSERT INTO DRC_MODEL (MOD_PRO_ID, MOD_TABLENAME) VALUES ({pro_id}, "{table_name}")'''.format(pro_id=proj_id, table_name=tab_name))
        mod_id = c.lastrowid

    #Create a Result row
    comment = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    c.execute('''INSERT INTO DRC_RUN_RESULTS (RUR_RUN_ID, RUR_MOD_ID, RUR_ROW_COUNT) VALUES ({run_id}, {mod_id}, {rowcnt})'''.format(run_id=run_id, mod_id=mod_id, rowcnt=row_count))

    conn.commit()

def get_model_info(project_name):
    '''
    Dump all models and their row counts to the screen
    '''
    from django.conf import settings
    from django.db.utils import DatabaseError
    from django.db.transaction import rollback_unless_managed
    from django.db import models

    with sqlite3.connect('./django-row-tracker-data/drtd.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SQLITE_VERSION()')
        data = cursor.fetchone()
        print 'SQLite version: ', data
        create_tables_if_necessary(conn)
        dic_id = initialize_for_this_run(conn, project_name)

        project_models = models.get_models(include_auto_created=True)

        for them in project_models:
            try:
                table_name = them._meta.db_table  
                row_count = them.objects.all().count()
                print table_name + " " + str(row_count)
                insert_run_result(conn, dic_id['proj_id'], dic_id['run_id'], table_name, row_count )
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
    parser.add_argument('--version', action='version', version='%(prog)s - Release : 1.1')
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
    get_model_info(args.project_name)


if __name__ == "__main__":
    main()

