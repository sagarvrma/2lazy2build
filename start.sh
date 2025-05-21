#!/bin/bash

# Install the necessary Playwright browsers
playwright install

# Start the Flask server (assuming it's in backend/app.py)
python backend/app.py
