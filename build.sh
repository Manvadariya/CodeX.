#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Navigate to the correct directory
cd CodeX

# Create the staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Collect static files and run migrations
python manage.py collectstatic --noinput --clear
python manage.py migrate

# Print debug information
echo "Static files directory content:"
ls -la staticfiles/
