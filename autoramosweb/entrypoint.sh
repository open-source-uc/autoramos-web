#!/bin/bash
celery -A autoramosweb beat &
celery -A autoramosweb worker -l info &
gunicorn autoramosweb.wsgi --bind 0.0.0.0:8000