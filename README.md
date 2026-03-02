# HR Communications Logs System

A Flask-based system for managing HR memos and communication logs.

## Features
- Create and track memos
- Log communication records
- Secretary dashboard view
- SQLite database

## Tech Stack
- Flask
- SQLAlchemy
- Flask-Migrate
- SQLite


To install, run the following upon cloning:

python -m venv venv

.\venv\Scripts\activate

pip install flask flask-sqlalchemy flask-login flask-migrate flask-wtf python-dotenv

pip freeze > requirements.txt

flask db init
flask db migrate -m "initial tables"
flask db upgrade
