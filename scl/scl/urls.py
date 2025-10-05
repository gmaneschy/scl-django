"""
URL configuration for scl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('cad_disciplina', views.cad_disciplina, name='cad_disciplina'),
    path('cad_turma', views.cad_turma, name='cad_turma'),
    path('cad_professor', views.cad_professor, name='cad_professor'),
    path('cad_aluno', views.cad_aluno, name='cad_aluno'),
    path('cad_funcionarios', views.cad_funcionarios, name='cad_funcionarios'),
    path('avisos', views.avisos, name='avisos'),
    path('professores', views.professores, name='professores'),
    path('financeiro', views.financeiro, name='financeiro'),
    path('relatorios', views.relatorios, name='relatorios'),
]
