#!/bin/bash

BIND="0.0.0.0:8000"

cd /fb2_srv && \
    gunicorn3 -e FLASK_ENV=prod --bind="${BIND}" --workers=4 'app:create_app()' --access-logfile -
