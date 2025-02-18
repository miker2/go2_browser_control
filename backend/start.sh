#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate go2-web-control
exec gunicorn --workers 1 --worker-class eventlet -b 127.0.0.1:5000 app:app