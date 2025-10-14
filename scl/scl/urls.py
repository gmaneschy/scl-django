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
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),

    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Cadastros - Diretoria
    path('cad_disciplina/', views.cad_disciplina, name='cad_disciplina'),
    path('cad_turma/', views.cad_turma, name='cad_turma'),
    path('cad_professor/', views.cad_professor, name='cad_professor'),
    path('cad_aluno/', views.cad_aluno, name='cad_aluno'),
    path('editar_aluno_responsavel/<int:aluno_id>/', views.editar_aluno_responsavel, name='editar_aluno_responsavel'),
    path('excluir_responsavel/<int:responsavel_id>/', views.excluir_responsavel, name='excluir_responsavel'),
    path('cad_funcionarios/', views.cad_funcionarios, name='cad_funcionarios'),

    # Gerenciamento de usuários
    path('redefinir_senha_professor/<int:professor_id>/', views.redefinir_senha_professor,
         name='redefinir_senha_professor'),
    path('redefinir_senha_aluno/<int:aluno_id>/', views.redefinir_senha_aluno, name='redefinir_senha_aluno'),
    path('criar_usuario_manual_professor/<int:professor_id>/', views.criar_usuario_manual_professor,
         name='criar_usuario_manual_professor'),
    path('criar_usuario_manual_aluno/<int:aluno_id>/', views.criar_usuario_manual_aluno,
         name='criar_usuario_manual_aluno'),

    # Sistema - Configurações
    path('config_sistema/', views.config_sistema, name='config_sistema'),

    # Avisos
    path('avisos/', views.avisos, name='avisos'),

    # Módulo Professores
    path('professores/', views.professores_dashboard, name='professores_dashboard'),
    path('professores/turmas/', views.professores_turmas, name='professores_turmas'),
    path('professores/turmas/<int:turma_id>/', views.professores_turmas, name='professores_turma_detalhe'),
    path('professores/aula/<int:aula_id>/presenca/', views.registrar_presenca, name='registrar_presenca'),
    path('professores/avaliacao/<int:avaliacao_id>/notas/', views.lancar_notas, name='lancar_notas'),
    path('professores/turma/<int:turma_id>/criar_avaliacao/', views.criar_avaliacao, name='criar_avaliacao'),

    # Módulo Financeiro
    path('financeiro/', views.financeiro, name='financeiro'),
    path('financeiro/contas_pagar/', views.contas_pagar, name='contas_pagar'),
    path('financeiro/contas_receber/', views.contas_receber, name='contas_receber'),

    # Módulo Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/turma/<int:turma_id>/', views.relatorio_turma, name='relatorio_turma'),
    path('relatorios/aluno/<int:aluno_id>/', views.relatorio_aluno, name='relatorio_aluno'),

    # URLs do Django Auth (para recuperação de senha)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]