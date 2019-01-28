#!/bin/bash -e

sed -i -e "s/\[ \"\$1\" = 'postgres' \]/[ 0 ]/" \
    /usr/local/bin/docker-entrypoint.sh
/usr/local/bin/docker-entrypoint.sh pg_ctl start

python3.7 -m data.initial_load
python3.7 -m server.app
