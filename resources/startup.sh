#!/bin/bash

gunicorn -k uvicorn.workers.UvicornWorker src.main:app --workers $(python3 src/scripts/get_workers_amount.py) --bind 0.0.0.0:8000