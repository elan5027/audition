#!/bin/sh
export ENV=prod

uvicorn app.main:app --reload