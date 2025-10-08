from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Count
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from .models import *
from .forms import *
import sentry_sdk

sentry_sdk.init(
    dsn="https://a69be57cee52a2a58d6985a410ba2777@o4509990068027392.ingest.us.sentry.io/4510125634813952",
    send_default_pii=True,
)

# Create your views here.
# Funções auxiliares para verificação de permissões
def is_diretoria(user):
    return user.groups.filter(name='Diretoria').exists()


def is_professor(user):
    return user.groups.filter(name='Professores').exists()


def is_aluno(user):
    return user.groups.filter(name='Alunos').exists()


# Views de Autenticação
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Redirecionar baseado no tipo de usuário
                if is_diretoria(user):
                    return redirect('cad_disciplina')
                elif is_professor(user):
                    return redirect('professores_dashboard')
                elif is_aluno(user):
                    return redirect('homepage')
                else:
                    return redirect('homepage')

        messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema.')
    return redirect('homepage')


@login_required
def profile(request):
    user = request.user
    context = {'user': user}

    try:
        if is_professor(user):
            professor = Professor.objects.get(usuario=user)
            context['perfil'] = professor
            context['tipo'] = 'professor'
        elif is_aluno(user):
            aluno = Aluno.objects.get(usuario=user)
            context['perfil'] = aluno
            context['tipo'] = 'aluno'
        elif is_diretoria(user):
            context['tipo'] = 'diretoria'
    except (Professor.DoesNotExist, Aluno.DoesNotExist):
        pass

    return render(request, 'profile.html', context)


# View para criação automática de usuários (para Diretoria)
@login_required
@user_passes_test(is_diretoria)
def criar_usuario_professor(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)

    if request.method == 'POST':
        # Criar usuário automaticamente
        username = professor.email.split('@')[0]  # Usa parte do email como username
        password = User.objects.make_random_password()

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=professor.email,
                password=password,
                first_name=professor.nome.split(' ')[0],
                last_name=' '.join(professor.nome.split(' ')[1:]) if len(professor.nome.split(' ')) > 1 else ''
            )

            # Adicionar ao grupo de Professores
            grupo_professores, created = Group.objects.get_or_create(name='Professores')
            user.groups.add(grupo_professores)

            # Vincular usuário ao professor
            professor.usuario = user
            professor.save()

            messages.success(request, f'Usuário criado para o professor. Senha: {password}')
        else:
            messages.error(request, 'Já existe um usuário com este username.')

    return redirect('cad_professor')


@login_required
@user_passes_test(is_diretoria)
def criar_usuario_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    if request.method == 'POST':
        # Criar usuário automaticamente
        username = aluno.email.split('@')[0]
        password = User.objects.make_random_password()

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=aluno.email,
                password=password,
                first_name=aluno.nome.split(' ')[0],
                last_name=' '.join(aluno.nome.split(' ')[1:]) if len(aluno.nome.split(' ')) > 1 else ''
            )

            # Adicionar ao grupo de Alunos
            grupo_alunos, created = Group.objects.get_or_create(name='Alunos')
            user.groups.add(grupo_alunos)

            # Vincular usuário ao aluno
            aluno.usuario = user
            aluno.save()

            messages.success(request, f'Usuário criado para o aluno. Senha: {password}')
        else:
            messages.error(request, 'Já existe um usuário com este username.')

    return redirect('cad_aluno')


# Views da Diretoria
@login_required
@user_passes_test(is_diretoria)
def cad_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Disciplina cadastrada com sucesso!')
            return redirect('cad_disciplina')
    else:
        form = DisciplinaForm()

    disciplinas = Disciplina.objects.all()
    return render(request, 'cad_disciplina.html', {
        'form': form,
        'disciplinas': disciplinas
    })


@login_required
@user_passes_test(is_diretoria)
def cad_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma cadastrada com sucesso!')
            return redirect('cad_turma')
    else:
        form = TurmaForm()

    turmas = Turma.objects.all()
    return render(request, 'cad_turma.html', {
        'form': form,
        'turmas': turmas
    })


@login_required
@user_passes_test(is_diretoria)
def cad_professor(request):
    if request.method == 'POST':
        form = ProfessorForm(request.POST)
        if form.is_valid():
            professor = form.save(commit=False)
            # Aqui você pode criar o usuário automaticamente se necessário
            professor.save()
            form.save_m2m()  # Para salvar relações ManyToMany
            messages.success(request, 'Professor cadastrado com sucesso!')
            return redirect('cad_professor')
    else:
        form = ProfessorForm()

    professores = Professor.objects.filter(ativo=True)
    return render(request, 'cad_professor.html', {
        'form': form,
        'professores': professores
    })


@login_required
@user_passes_test(is_diretoria)
def cad_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save(commit=False)
            aluno.save()
            form.save_m2m()
            messages.success(request, 'Aluno cadastrado com sucesso!')
            return redirect('cad_aluno')
    else:
        form = AlunoForm()

    alunos = Aluno.objects.filter(ativo=True)
    return render(request, 'cad_aluno.html', {
        'form': form,
        'alunos': alunos
    })


@login_required
@user_passes_test(is_diretoria)
def cad_responsavel(request):
    if request.method == 'POST':
        form = ResponsavelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Responsável cadastrado com sucesso!')
            return redirect('cad_responsavel')
    else:
        form = ResponsavelForm()

    responsaveis = Responsavel.objects.all()
    return render(request, 'cad_responsavel.html', {
        'form': form,
        'responsaveis': responsaveis
    })


@login_required
@user_passes_test(is_diretoria)
def cad_funcionarios(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('cad_funcionarios')
    else:
        form = FuncionarioForm()

    funcionarios = Funcionario.objects.filter(ativo=True)
    return render(request, 'cad_funcionarios.html', {
        'form': form,
        'funcionarios': funcionarios
    })


# Views dos Professores
@login_required
@user_passes_test(is_professor)
def professores_dashboard(request):
    try:
        professor = Professor.objects.get(usuario=request.user)
        turmas = professor.turmas.all()
        disciplinas = professor.disciplinas.all()

        return render(request, 'professores/dashboard.html', {
            'professor': professor,
            'turmas': turmas,
            'disciplinas': disciplinas
        })
    except Professor.DoesNotExist:
        messages.error(request, 'Perfil de professor não encontrado.')
        return redirect('homepage')


@login_required
@user_passes_test(is_professor)
def professores_turmas(request, turma_id=None):
    professor = Professor.objects.get(usuario=request.user)

    if turma_id:
        turma = get_object_or_404(Turma, id=turma_id)
        alunos = turma.aluno_set.all()
        aulas = Aula.objects.filter(turma=turma, professor=professor)

        return render(request, 'professores/turma_detalhe.html', {
            'turma': turma,
            'alunos': alunos,
            'aulas': aulas,
            'professor': professor
        })

    turmas = professor.turmas.all()
    return render(request, 'professores/turmas.html', {
        'turmas': turmas,
        'professor': professor
    })


@login_required
@user_passes_test(is_professor)
def registrar_presenca(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id)
    professor = Professor.objects.get(usuario=request.user)

    if aula.professor != professor:
        messages.error(request, 'Você não tem permissão para acessar esta aula.')
        return redirect('professores_turmas')

    alunos = aula.turma.aluno_set.all()

    if request.method == 'POST':
        for aluno in alunos:
            situacao = request.POST.get(f'situacao_{aluno.id}')
            observacao = request.POST.get(f'observacao_{aluno.id}', '')

            presenca, created = Presenca.objects.get_or_create(
                aula=aula,
                aluno=aluno,
                defaults={'situacao': situacao, 'observacao': observacao}
            )

            if not created:
                presenca.situacao = situacao
                presenca.observacao = observacao
                presenca.save()

        messages.success(request, 'Presenças registradas com sucesso!')
        return redirect('professores_turmas')

    presencas = Presenca.objects.filter(aula=aula)
    presenca_dict = {p.aluno.id: p for p in presencas}

    return render(request, 'professores/registrar_presenca.html', {
        'aula': aula,
        'alunos': alunos,
        'presenca_dict': presenca_dict
    })


@login_required
@user_passes_test(is_professor)
def lancar_notas(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    professor = Professor.objects.get(usuario=request.user)

    if avaliacao.professor != professor:
        messages.error(request, 'Você não tem permissão para acessar esta avaliação.')
        return redirect('professores_turmas')

    alunos = avaliacao.turma.aluno_set.all()

    if request.method == 'POST':
        for aluno in alunos:
            nota_valor = request.POST.get(f'nota_{aluno.id}')
            observacao = request.POST.get(f'observacao_{aluno.id}', '')

            if nota_valor:
                nota, created = Nota.objects.get_or_create(
                    avaliacao=avaliacao,
                    aluno=aluno,
                    defaults={'nota': nota_valor, 'observacao': observacao}
                )

                if not created:
                    nota.nota = nota_valor
                    nota.observacao = observacao
                    nota.save()

        messages.success(request, 'Notas lançadas com sucesso!')
        return redirect('professores_turmas')

    notas = Nota.objects.filter(avaliacao=avaliacao)
    nota_dict = {n.aluno.id: n for n in notas}

    return render(request, 'professores/lancar_notas.html', {
        'avaliacao': avaliacao,
        'alunos': alunos,
        'nota_dict': nota_dict
    })


@login_required
@user_passes_test(is_professor)
def criar_avaliacao(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    professor = Professor.objects.get(usuario=request.user)

    if turma not in professor.turmas.all():
        messages.error(request, 'Você não tem permissão para criar avaliações nesta turma.')
        return redirect('professores_turmas')

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.professor = professor
            avaliacao.save()
            messages.success(request, 'Avaliação criada com sucesso!')
            return redirect('professores_turmas')
    else:
        form = AvaliacaoForm(initial={'turma': turma, 'professor': professor})

    return render(request, 'professores/criar_avaliacao.html', {
        'form': form,
        'turma': turma
    })


# Views do Financeiro
@login_required
@user_passes_test(is_diretoria)
def financeiro(request):
    contas_pagar = ContaPagar.objects.all()
    contas_receber = ContaReceber.objects.all()

    total_a_pagar = sum(conta.valor for conta in contas_pagar.filter(pago=False))
    total_a_receber = sum(conta.valor for conta in contas_receber.filter(recebido=False))

    return render(request, 'financeiro/dashboard.html', {
        'contas_pagar': contas_pagar,
        'contas_receber': contas_receber,
        'total_a_pagar': total_a_pagar,
        'total_a_receber': total_a_receber
    })


@login_required
@user_passes_test(is_diretoria)
def contas_pagar(request):
    if request.method == 'POST':
        form = ContaPagarForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta a pagar cadastrada com sucesso!')
            return redirect('contas_pagar')
    else:
        form = ContaPagarForm()

    contas = ContaPagar.objects.all()
    return render(request, 'financeiro/contas_pagar.html', {
        'form': form,
        'contas': contas
    })


@login_required
@user_passes_test(is_diretoria)
def contas_receber(request):
    if request.method == 'POST':
        form = ContaReceberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta a receber cadastrada com sucesso!')
            return redirect('contas_receber')
    else:
        form = ContaReceberForm()

    contas = ContaReceber.objects.all()
    return render(request, 'financeiro/contas_receber.html', {
        'form': form,
        'contas': contas
    })


# Views de Relatórios
@login_required
@user_passes_test(is_diretoria)
def relatorios(request):
    turmas = Turma.objects.all()
    return render(request, 'relatorios/dashboard.html', {
        'turmas': turmas
    })


@login_required
@user_passes_test(is_diretoria)
def relatorio_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    alunos = turma.aluno_set.all()

    # Estatísticas da turma
    total_alunos = alunos.count()

    # Aqui você pode adicionar mais cálculos de estatísticas
    # como médias de notas, presenças, etc.

    return render(request, 'relatorios/turma.html', {
        'turma': turma,
        'alunos': alunos,
        'total_alunos': total_alunos
    })


@login_required
@user_passes_test(is_diretoria)
def relatorio_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    # Buscar notas e presenças do aluno
    notas = Nota.objects.filter(aluno=aluno)
    presencas = Presenca.objects.filter(aluno=aluno)

    # Calcular médias
    if notas.exists():
        media_geral = notas.aggregate(Avg('nota'))['nota__avg']
    else:
        media_geral = 0

    total_presencas = presencas.filter(situacao='presente').count()
    total_faltas = presencas.filter(situacao='falta').count()
    total_faltas_justificadas = presencas.filter(situacao='falta_justificada').count()
    total_aulas = presencas.count()

    if total_aulas > 0:
        percentual_presenca = (total_presencas / total_aulas) * 100
    else:
        percentual_presenca = 0

    return render(request, 'relatorios/aluno.html', {
        'aluno': aluno,
        'notas': notas,
        'presencas': presencas,
        'media_geral': media_geral,
        'percentual_presenca': percentual_presenca,
        'total_presencas': total_presencas,
        'total_faltas': total_faltas,
        'total_faltas_justificadas': total_faltas_justificadas
    })


# Views de Avisos
@login_required
def avisos(request):
    user = request.user

    if is_diretoria(user):
        # Diretoria pode ver e criar todos os avisos
        avisos_list = Aviso.objects.all()
        if request.method == 'POST':
            form = AvisoForm(request.POST)
            if form.is_valid():
                aviso = form.save(commit=False)
                aviso.enviado_por = user
                aviso.save()
                form.save_m2m()
                messages.success(request, 'Aviso criado com sucesso!')
                return redirect('avisos')
        else:
            form = AvisoForm()
    elif is_professor(user):
        # Professores veem apenas avisos relevantes para eles
        try:
            professor = Professor.objects.get(usuario=user)
            avisos_list = Aviso.objects.filter(
                destinatarios_professores=professor
            ) | Aviso.objects.filter(
                destinatarios_turmas__in=professor.turmas.all()
            ).distinct()
        except Professor.DoesNotExist:
            avisos_list = Aviso.objects.none()
        form = None
    else:
        # Alunos veem apenas avisos relevantes para eles
        try:
            aluno = Aluno.objects.get(usuario=user)
            avisos_list = Aviso.objects.filter(
                destinatarios_alunos=aluno
            ) | Aviso.objects.filter(
                destinatarios_turmas__in=aluno.turmas.all()
            ).distinct()
        except Aluno.DoesNotExist:
            avisos_list = Aviso.objects.none()
        form = None

    return render(request, 'avisos.html', {
        'avisos': avisos_list,
        'form': form,
        'user': user
    })


# View para configurações do sistema
@login_required
@user_passes_test(is_diretoria)
def config_sistema(request):
    sisprof, created = SisProf.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = SisProfConfigForm(request.POST, request.FILES, instance=sisprof)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('config_sistema')
    else:
        form = SisProfConfigForm(instance=sisprof)

    return render(request, 'config_sistema.html', {'form': form})