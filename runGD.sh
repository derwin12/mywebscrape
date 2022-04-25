#!/bin/bash
#
# 30 19 * * 0 cd /home/pi/mywebscrape; bash ./runGD.sh > /tmp/logit 2>&1
#
source /home/pi/.asdf/asdf.sh
echo $PYTHONPATH
export PYTHONPATH=/home/pi/.asdf/shims/python:.
python -V
python scrapers/gdNew.py