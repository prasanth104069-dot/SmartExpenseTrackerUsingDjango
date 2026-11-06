from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("add/", views.add_expense, name="add_expense"),
    path("edit/<int:pk>/", views.edit_expense, name="edit_expense"),
    path("delete/<int:pk>/", views.delete_expense, name="delete_expense"),
    path("predict/", views.predict_category_api, name="predict_category"),
    path("report/", views.download_report, name="download_report"),
]
