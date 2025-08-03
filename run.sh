#!/bin/bash

gunicorn --bind 0.0.0.0:5555 -w 4 --threads 4 main:http --certfile=cert.pem --keyfile=key.pem
# gunicorn --bind 0.0.0.0:5555 -w 4 --threads 4 main:http