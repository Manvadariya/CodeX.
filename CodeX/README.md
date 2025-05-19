# CodeX

A Django-based application for coding and execution. This application supports multiple programming languages including Python, Java, C++, and JavaScript.

## Features

- User authentication with Google
- Code editor
- Code execution for multiple languages
- User dashboard

## Deployment

This application is configured for deployment on Render.com.

**Important Note on Database:** For production on Render, ensure you configure a production-grade database (e.g., PostgreSQL, often provided by Render). SQLite is used for local development only and is not suitable for production. Your `render.yaml` or Render service settings should reflect the production database configuration.

### Deployment Steps

1. Push this repository to GitHub
2. Connect your GitHub repository to Render
3. Create a new Web Service on Render with the following settings:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn CodeX.wsgi:application`
   - Select the appropriate environment variables (they are defined in render.yaml)

## Local Development

To run this project locally:

1. Install dependencies: `pip install -r requirements.txt`
2. **Set up your local database (SQLite is configured by default for development).**
3. Make migrations: `python manage.py migrate`
4. Run the development server: `python manage.py runserver`

## Technologies Used

- Django
- SQLite (local development)
- Google Authentication
- Gunicorn (for production)
- WhiteNoise (for static files in production)
