#!/bin/sh
export ENV=prod

poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
