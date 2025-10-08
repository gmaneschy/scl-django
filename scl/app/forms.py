from django import forms
from .models import *


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'disciplinas': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'turno': forms.TextInput(attrs={'class': 'form-control'}),
            'sala': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'disciplinas': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Para ManyToMany
        }

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Para ManyToMany
            'r_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'r_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'r_telefone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'r_nome': 'Nome do Responsável',
            'r_email': 'Email do Responsável',
            'r_telefone': 'Telefone do Responsável',
        }

class SisProf(forms.ModelForm):
    class Meta:
        model = SisProf
        fields = '__all__'
        widgets = {
        }