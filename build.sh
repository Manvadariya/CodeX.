#!/usr/bin/env bash
# exit on error
set -o errexit

# Set RENDER environment variable
export RENDER=True

cd CodeX
pip install -r ../requirements.txt

# Debug: Print current directory and Python version
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Debug: List static directory contents before collectstatic
echo "Contents of static directory before:" 
ls -la static/ || echo "No static directory yet"

# Create staticfiles directory explicitly with full permissions
mkdir -p staticfiles
chmod -R 755 staticfiles
echo "Created staticfiles directory"

# Run collectstatic with verbosity
python manage.py collectstatic --no-input --verbosity 2
echo "Collectstatic completed"

# Debug: Check staticfiles directory after collectstatic
echo "Contents of staticfiles directory after:" 
ls -la staticfiles/ || echo "Still no staticfiles content"

# Run migrations
python manage.py migrate
echo "Migrations completed"
