#!/bin/sh

set -e
cd /app

python -m db.wait_for_db

alembic upgrade head

exec python main.py
