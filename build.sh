#!/usr/bin/env bash
# File: D:/CodeX/build.sh
# exit on error
set -o errexit

echo "Starting build process..."

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Navigating to Django project directory..."
cd CodeX

echo "Creating staticfiles directory if it doesn't exist..."
mkdir -p staticfiles

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput --clear

echo "Running Django migrations..."
python manage.py migrate

echo "Checking staticfiles directory content..."
ls -la staticfiles/

echo "Build process finished."