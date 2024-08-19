#!/bin/sh

alembic upgrade head

# Probably init some data here???
python /workspace/app/scripts/init_db.py

exec "$@"