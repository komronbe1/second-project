from django import forms
from card.models import User, Card

class ExcelImport(forms.Form):
    excel_file =  forms.FileField()