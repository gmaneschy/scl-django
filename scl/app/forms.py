from django import forms
from .models import *

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            'ano_letivo': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        exclude = ['usuario']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.NumberInput(attrs={'class': 'form-control'}),
            'disciplinas': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'tipo_notificacao': forms.Select(attrs={'class': 'form-control'}),
        }

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        exclude = ['usuario']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.NumberInput(attrs={'class': 'form-control'}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'tipo_notificacao': forms.Select(attrs={'class': 'form-control'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco': forms.TextInput(attrs={'class': 'form-control'}),
            'email_responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone_responsavel': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_notificacao_responsavel': forms.Select(attrs={'class': 'form-control'}),
        }


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        exclude = ['usuario']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.NumberInput(attrs={'class': 'form-control'}),
            'cargo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_notificacao': forms.Select(attrs={'class': 'form-control'}),
        }

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = '__all__'
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-control'}),
            'disciplina': forms.Select(attrs={'class': 'form-control'}),
            'professor': forms.Select(attrs={'class': 'form-control'}),
            'data_aula': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class PresencaForm(forms.ModelForm):
    class Meta:
        model = Presenca
        fields = ['situacao', 'observacao']
        widgets = {
            'situacao': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = '__all__'
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-control'}),
            'disciplina': forms.Select(attrs={'class': 'form-control'}),
            'professor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_avaliacao': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_avaliacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['nota', 'observacao']
        widgets = {
            'nota': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class AvisoForm(forms.ModelForm):
    class Meta:
        model = Aviso
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'tipo_aviso': forms.Select(attrs={'class': 'form-control'}),
            'data_envio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'enviado_por': forms.HiddenInput(),
            'destinatarios_turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'destinatarios_alunos': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'destinatarios_professores': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class ContaPagarForm(forms.ModelForm):
    class Meta:
        model = ContaPagar
        fields = '__all__'
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ContaReceberForm(forms.ModelForm):
    class Meta:
        model = ContaReceber
        fields = '__all__'
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_recebimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SisProfConfigForm(forms.ModelForm):
    class Meta:
        model = SisProf
        fields = '__all__'
        widgets = {
            'nome_escola': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_letivo_atual': forms.NumberInput(attrs={'class': 'form-control'}),
        }