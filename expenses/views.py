import csv
import io
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ExpenseForm, SignUpForm
from .models import Expense
from .utils import predict_category

PERIODS = [("today", "Today"), ("week", "This Week"), ("month", "This Month"), ("all", "All Time")]


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})


def _filtered_expenses(request):
    """Return (queryset, period) limited to the logged-in user and chosen period."""
    period = request.GET.get("period", "month")
    if period not in dict(PERIODS):
        period = "month"
    today = timezone.localdate()
    qs = Expense.objects.filter(user=request.user)
    if period == "today":
        qs = qs.filter(date=today)
    elif period == "week":
        start = today - timedelta(days=today.weekday())  # Monday
        qs = qs.filter(date__range=(start, today))
    elif period == "month":
        qs = qs.filter(date__year=today.year, date__month=today.month)
    return qs, period


@login_required
def dashboard(request):
    qs, period = _filtered_expenses(request)
    total = qs.aggregate(t=Sum("amount"))["t"] or 0
    by_category = list(
        qs.values("category").annotate(total=Sum("amount"), n=Count("id")).order_by("-total")
    )
    by_date = list(qs.values("date").annotate(total=Sum("amount")).order_by("date"))

    chart_data = {
        "cat_labels": [c["category"] for c in by_category],
        "cat_values": [float(c["total"]) for c in by_category],
        "date_labels": [d["date"].strftime("%d %b") for d in by_date],
        "date_values": [float(d["total"]) for d in by_date],
    }
    context = {
        "expenses": qs,
        "total": total,
        "count": qs.count(),
        "top_category": by_category[0] if by_category else None,
        "period": period,
        "periods": PERIODS,
        "chart_data": chart_data,
    }
    return render(request, "expenses/dashboard.html", context)


@login_required
def add_expense(request):
    form = ExpenseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        messages.success(request, f"Expense added under {expense.category}.")
        return redirect("dashboard")
    return render(request, "expenses/expense_form.html", {"form": form, "title": "Add expense"})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense)  # pre-fills original data
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Expense updated.")
        return redirect("dashboard")
    return render(request, "expenses/expense_form.html", {"form": form, "title": "Edit expense"})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted.")
        return redirect("dashboard")
    return render(request, "expenses/expense_confirm_delete.html", {"expense": expense})


@login_required
def predict_category_api(request):
    return JsonResponse({"category": predict_category(request.GET.get("q", ""))})


@login_required
def download_report(request):
    qs, period = _filtered_expenses(request)
    fmt = request.GET.get("format", "csv")
    total = qs.aggregate(t=Sum("amount"))["t"] or 0
    filename = f"expenses_{period}_{timezone.localdate()}"

    if fmt == "pdf":
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError:
            return HttpResponse("PDF export needs reportlab: pip install reportlab", status=500)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, title="Expense Report")
        styles = getSampleStyleSheet()
        rows = [["Date", "Description", "Category", "Amount (Rs.)"]]
        for e in qs:
            rows.append([e.date.strftime("%d-%m-%Y"), e.description[:40], e.category, f"{e.amount:.2f}"])
        rows.append(["", "", "Total", f"{total:.2f}"])

        table = Table(rows, repeatRows=1, colWidths=[80, 200, 100, 90])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ALIGN", (3, 0), (3, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f2f6ff")]),
        ]))
        label = dict(PERIODS)[period]
        doc.build([
            Paragraph(f"Expense Report - {request.user.username}", styles["Title"]),
            Paragraph(f"Period: {label} | Generated: {timezone.localdate():%d %b %Y}", styles["Normal"]),
            Spacer(1, 14),
            table,
        ])
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
        return response

    response = HttpResponse(content_type="text/csv")
    
    if fmt == "xlsx":
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill
        except ImportError:
            return HttpResponse("Excel export needs openpyxl: pip install openpyxl", status=500)

        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"
        ws.append(["Date", "Description", "Category", "Amount", "Notes"])
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="0D1B2A")
        for e in qs:
            ws.append([e.date, e.description, e.category, float(e.amount), e.notes])
        ws.append(["", "", "Total", float(total), ""])
        ws.cell(row=ws.max_row, column=3).font = Font(bold=True)
        ws.cell(row=ws.max_row, column=4).font = Font(bold=True)
        for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
            for c in row:
                c.number_format = "DD-MMM-YYYY"
        for col, width in zip("ABCDE", [15, 36, 16, 14, 40]):
            ws.column_dimensions[col].width = width
        ws.freeze_panes = "A2"

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
        wb.save(response)
        return response
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Date", "Description", "Category", "Amount", "Notes"])
    for e in qs:
        writer.writerow([e.date, e.description, e.category, e.amount, e.notes])
    writer.writerow(["", "", "Total", total, ""])
    return response
