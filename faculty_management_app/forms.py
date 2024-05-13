from django import forms
from django.forms import Form
from faculty_management_app.models import Courses, SessionYearModel


class DateInput(forms.DateInput):
    input_type = "date"
