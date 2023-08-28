# Online Cinema Repository README

## Overview
The repository is a Django-based project for an online cinema platform. It uses PostgreSQL as the database and follows the Django project structure.

## Prerequisites
- Python 3.x
- Django 3.2
- PostgreSQL

## Installation

### Clone the Repository
```bash
git clone https://github.com/dmshirochenko/online_cinema.git
```

### Environment Setup
```bash
.env.example to .env and update the variables.
```
```bash
cp config/.env.example config/.env
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Database Setup
Update the .env file with your PostgreSQL credentials.
Run migrations:
```bash
python manage.py migrate
```

### Running the Project
Start the Django development server:

```bash
python manage.py runserver
```

Project Structure
config/: Contains core settings and configurations.
movies/: Contains the main app logic, models, and views.
requirements.txt: Lists project dependencies.