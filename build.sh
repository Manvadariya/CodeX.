#!/usr/bin/env bash
# File: D:/CodeX/build.sh
# exit on error
set -o errexit

cd CodeX
pip install -r ../requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Print debug information
echo "Static files directory content:"
ls -la staticfiles/

echo "Checking staticfiles directory content..."
ls -la staticfiles/

echo "Build process finished."