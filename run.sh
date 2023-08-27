#!/usr/bin/env bash
export FLASK_APP=hello.py
# 启用重载器
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=80