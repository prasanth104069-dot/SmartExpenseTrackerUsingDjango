# Smart Expense Tracker

A lightweight Django web app that helps you record, categorise and analyse your daily, weekly and monthly spending. Each user has a private account, and the app predicts the category of an expense from its description.

## Features

- **User authentication**: signup, login and logout; each user sees only their own data
- **Add, edit and delete expenses**: edit pre-fills the form; delete asks for confirmation
- **Smart category prediction**: keyword matching (for example "uber" becomes Travel, "pizza" becomes Food)
- **Date filters**: Today, This Week, This Month and All Time
- **Charts**: doughnut chart (spending by category) and bar chart (spending per day) using Chart.js
- **Download reports**: export the filtered expenses as CSV, PDF or Excel (.xlsx)
- **Responsive UI**: clean Bootstrap-based interface that works on phones and laptops

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django |
| Database | SQLite |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Charts | Chart.js |
| Reports | csv, ReportLab, openpyxl |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/smart-expense-tracker.git
cd smart-expense-tracker
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

```bash
python manage.py makemigrations expenses
python manage.py migrate
```

### 5. Run the server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ and click **Sign up** to create an account.

(Optional) Create an admin user for `/admin/`:

```bash
python manage.py createsuperuser
```

## Project Structure

```
smart-expense-tracker/
├── manage.py
├── requirements.txt
├── smart_tracker/        # project settings and root URLs
│   ├── settings.py
│   └── urls.py
├── expenses/             # main app
│   ├── models.py         # Expense table
│   ├── forms.py          # expense and signup forms
│   ├── views.py          # dashboard, CRUD, reports
│   ├── urls.py           # app routes
│   ├── utils.py          # keyword category prediction
│   └── static/expenses/app.css
└── templates/            # HTML pages
    ├── base.html
    ├── registration/     # login and signup
    └── expenses/         # dashboard, form, delete confirmation
```

## How Category Prediction Works

The description is lower-cased and matched against a dictionary of keywords in `expenses/utils.py`. The first matching category is used; if nothing matches, the expense is saved as **Other**.

| Category | Example keywords |
|---|---|
| Food | pizza, lunch, swiggy, coffee |
| Travel | uber, taxi, metro, petrol |
| Shopping | amazon, shirt, mall |
| Bills | electricity, wifi, rent, recharge |
| Entertainment | netflix, spotify, cinema |
| Health | doctor, medicine, gym |
| Education | course, book, tuition |

To add your own keywords, edit the `KEYWORDS` dictionary in `expenses/utils.py`.

## Screenshots

_Add screenshots of the dashboard, add-expense form and reports here._

## Future Improvements

- Machine-learning based category prediction
- Monthly budget limits with alerts
- Recurring expenses and bill reminders
- Custom categories and user-editable keywords
- Receipt upload with OCR
- Deployment with PostgreSQL

## Author

**Prasanth**

## License

This project is for educational purposes.
