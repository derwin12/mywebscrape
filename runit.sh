#!/bin/bash
#
# 30 19 * * * cd /home/pi/mywebscrape; bash ./runit.sh > /tmp/logit 2>&1
#
source /home/pi/.asdf/asdf.sh
echo $PYTHONPATH
export PYTHONPATH=/home/pi/.asdf/shims/python:.
python -V
python app/run_scrapers.py