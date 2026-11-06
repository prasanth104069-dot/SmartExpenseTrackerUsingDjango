from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CATEGORY_CHOICES, Expense
from .utils import predict_category


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class ExpenseForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=[("", "Auto-detect (smart)")] + CATEGORY_CHOICES, required=False
    )

    class Meta:
        model = Expense
        fields = ["description", "amount", "category", "date", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-select" if name == "category" else "form-control"
            field.widget.attrs["class"] = css
        self.fields["description"].widget.attrs["placeholder"] = "e.g. Uber to office"
        self.fields["amount"].widget.attrs["step"] = "0.01"

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("category"):
            cleaned["category"] = predict_category(cleaned.get("description", ""))
        return cleaned
