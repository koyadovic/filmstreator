#!/bin/bash

# export DJANGO_SETTINGS_MODULE=filmstreator.settings.production

cd ..
source ../bin/activate
python manage.py startticker
