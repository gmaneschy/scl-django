from django import forms
from .models import *


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = '__all__'

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = '__all__'
        widgets = {
            'disciplinas': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = '__all__'
        widgets = {
            'disciplinas': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }