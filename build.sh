#!/bin/bash
pip install -r requirements.txt
PLAYWRIGHT_BROWSERS_PATH=/tmp/pw python -m playwright install chromium
