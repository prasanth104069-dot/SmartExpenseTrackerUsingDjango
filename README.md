# Smart Expense Tracker (Django)

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations expenses
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```
Open http://127.0.0.1:8000/ and sign up.

## Structure
- `smart_tracker/` - project settings and root URLs
- `expenses/` - models, forms, views, keyword category prediction (`utils.py`)
- `templates/` - Bootstrap 5 pages; Chart.js charts load from a CDN

Set `TIME_ZONE` in `smart_tracker/settings.py` to your timezone.
