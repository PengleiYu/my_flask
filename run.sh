#!/usr/bin/env bash
export FLASK_APP=flask2.py
# 启用重载器
export FLASK_DEBUG=1
source env.sh
flask run --host=0.0.0.0 --port=80 &