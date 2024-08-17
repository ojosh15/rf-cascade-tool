#!/bin/sh

alembic upgrade head

# Probably init some data here???

exec "$@"