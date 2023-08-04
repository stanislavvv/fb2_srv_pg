#!/bin/bash

BIND="0.0.0.0:8000"
gunicorn3 -e FLASK_ENV=prod --bind="${BIND}" --timeout 600 --workers=3 'app:create_app()' --access-logfile -
