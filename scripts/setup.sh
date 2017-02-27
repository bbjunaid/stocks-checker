#!/usr/bin/env bash

set -e

rm -rf virtualenv

virtualenv virtualenv

source virtualenv/bin/activate

#env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include"
pip install -r requirements.txt
