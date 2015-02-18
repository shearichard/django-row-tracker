import sys

from django.core.management import setup_environ

import settings
setup_environ(settings)

from django.db.utils import DatabaseError

from django.db.transaction import rollback_unless_managed
from django.db import models

def get_model_info():
    '''
    Dump all models and their row counts to the screen
    '''
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

def main():
    '''
    Handle main processing
    '''
    get_model_info()


if __name__ == "__main__":
    main()

