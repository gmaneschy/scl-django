from django.shortcuts import render, redirect
from .models import *
from .forms import *
import sentry_sdk

sentry_sdk.init(
    dsn="https://a69be57cee52a2a58d6985a410ba2777@o4509990068027392.ingest.us.sentry.io/4510125634813952",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def cad_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save(commit=False)
            """disciplina.usuario = request.user"""
            disciplina.save()
            return redirect('cad_disciplina')
    else:
        form = DisciplinaForm()
    return render(request, 'cad_disciplina.html', {'form': form})

def cad_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save(commit=False)
            """turma.usuario = request.user"""
            turma.save()
            return redirect('cad_turma')
    else:
        form = TurmaForm()
    return render(request, 'cad_turma.html', {'form': form})

def cad_professor(request):
    if request.method == 'POST':
        form = ProfessorForm(request.POST)
        if form.is_valid():
            professor = form.save(commit=False)
            """professor.usuario = request.user"""
            professor.save()
            return redirect('cad_professor')
    else:
        form = ProfessorForm()
    return render(request, 'cad_professor.html', {'form': form})

def cad_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save(commit=False)
            """aluno.usuario = request.user"""
            aluno.save()
            return redirect('cad_aluno')
    else:
        form = AlunoForm()
    return render(request, 'cad_aluno.html', {'form': form})

def cad_funcionarios(request):
    return render(request, 'cad_funcionarios.html')

def professores(request):
    """professor.usuario = request.user"""
    if request.method == 'POST':
        form = SisProf(request.GET, request.POST)
        if form.is_valid():
            sisprof = form.save(commit=False)
            sisprof.save()
            return redirect('professores')
    else:
        form = SisProf()
    return render(request, 'professores.html', {'form': form})

def financeiro(request):
    return render(request, 'financeiro.html')

def relatorios(request):
    return render(request, 'relatorios.html')

def avisos(request):
    return render(request, 'avisos.html')