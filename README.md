django-row-counter
=========

Overview
--------
A stand-alone script which may be used to use row counts in all the models within a given Django project.

Each time the script is a row count for each model in each Application of the Project of interest and the results are written to a SQLite database.

Each run is timestamped and the user is able to supply a comment describing the situation for each run.

Multiple projects may be tracked within the same database.

Version 
--------
1.1.


Running 
--------
The script is run as follows where `path-to-project-root` is the file path to the root of the project of interest relative to the location of `django-row-tracker.py`; and `project-name` is the name of the Django project of interest.

> python django-row-tracker.py path-to-project-root project-name 

A directory with the name `django-row-tracker-data` should be created within the directory `django-row-tracker.py` is in to hold the SQLite database used to hold the results.
