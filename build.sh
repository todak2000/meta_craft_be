#!/usr/bin/env bash
# exit on error
set -o errexit

# poetry install
pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --username daniel --password adminadmin --noinput --email 'daniel@email.com'