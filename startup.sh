#!/bin/bash
ip l set down wlan1
cd /opt/warpi
source /opt/warpi/venv/bin/activate
python warpigui.py