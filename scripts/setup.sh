#!/usr/bin/env bash

set -e

rm -rf virtualenv

virtualenv virtualenv

source virtualenv/bin/activate

pip install -r requirements.txt
