from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Count
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
import random
import string
from .models import *
from .forms import *


# Funções auxiliares para verificação de permissões
def is_diretoria(user):
    return user.groups.filter(name='Diretoria').exists()


def is_professor(user):
    return user.groups.filter(name='Professores').exists()


def is_aluno(user):
    return user.groups.filter(name='Alunos').exists()


def gerar_senha_automatica(tamanho=8):
    """Gera uma senha aleatória"""
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))


def criar_usuario_automatico(email, nome, grupo_nome):
    """Cria um usuário automaticamente baseado no email e nome"""
    try:
        # Usa parte do email como username (antes do @)
        username = email.split('@')[0].lower()

        # Verifica se username já existe, se sim, adiciona número
        base_username = username
        contador = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{contador}"
            contador += 1

        # Gera senha automática
        senha = gerar_senha_automatica()

        # Cria o usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha,
            first_name=nome.split(' ')[0],
            last_name=' '.join(nome.split(' ')[1:]) if len(nome.split(' ')) > 1 else ''
        )

        # Adiciona ao grupo apropriado
        grupo, created = Group.objects.get_or_create(name=grupo_nome)
        user.groups.add(grupo)

        return user, senha

    except Exception as e:
        print(f"Erro ao criar usuário automático: {e}")
        return None, None


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
                    return redirect('aluno')
                else:
                    return redirect('login')

        messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema.')
    return redirect('login')


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
            try:
                professor = form.save(commit=False)

                # Cria usuário automaticamente se não existir
                if not professor.usuario:
                    usuario, senha = criar_usuario_automatico(
                        professor.email,
                        professor.nome,
                        'Professores'
                    )

                    if usuario:
                        professor.usuario = usuario
                        professor.save()
                        form.save_m2m()

                        messages.success(
                            request,
                            f'Professor cadastrado com sucesso! '
                            f'Usuário: {usuario.username} | Senha: {senha}'
                        )
                    else:
                        professor.save()
                        form.save_m2m()
                        messages.warning(
                            request,
                            'Professor cadastrado, mas não foi possível criar o usuário automático.'
                        )
                else:
                    professor.save()
                    form.save_m2m()
                    messages.success(request, 'Professor atualizado com sucesso!')

                return redirect('cad_professor')

            except Exception as e:
                messages.error(request, f'Erro ao cadastrar professor: {str(e)}')
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
    aluno_form = AlunoForm(request.POST or None)
    responsavel_form = ResponsavelForm(request.POST or None)

    if request.method == 'POST':
        if aluno_form.is_valid() and responsavel_form.is_valid():
            try:
                # Salvar o aluno primeiro
                aluno = aluno_form.save(commit=False)

                # Criar usuário automaticamente para o aluno
                if not aluno.usuario:
                    usuario_aluno, senha_aluno = criar_usuario_automatico(
                        aluno.email,
                        aluno.nome,
                        'Alunos'
                    )
                    if usuario_aluno:
                        aluno.usuario = usuario_aluno

                aluno.save()
                aluno_form.save_m2m()  # Para salvar as turmas (ManyToMany)

                # Agora salvar o responsável vinculado ao aluno
                responsavel = responsavel_form.save(commit=False)
                responsavel.aluno = aluno  # Vincular o responsável ao aluno

                # Criar usuário automaticamente para o responsável
                if not responsavel.usuario:
                    usuario_responsavel, senha_responsavel = criar_usuario_automatico(
                        responsavel.email,
                        responsavel.nome,
                        'Responsaveis'
                    )
                    if usuario_responsavel:
                        responsavel.usuario = usuario_responsavel

                responsavel.save()

                messages.success(
                    request,
                    f'Aluno e responsável cadastrados com sucesso! '
                    f'Aluno: {usuario_aluno.username if usuario_aluno else aluno.email} | '
                    f'Senha Aluno: {senha_aluno if usuario_aluno else "Usuário não criado"} | '
                    f'Responsável: {usuario_responsavel.username if usuario_responsavel else responsavel.email} | '
                    f'Senha Responsável: {senha_responsavel if usuario_responsavel else "Usuário não criado"}'
                )
                return redirect('cad_aluno')

            except Exception as e:
                messages.error(request, f'Erro ao cadastrar aluno e responsável: {str(e)}')
        else:
            # Se algum formulário for inválido, mostrar erros
            messages.error(request, 'Por favor, corrija os erros no formulário.')

    alunos = Aluno.objects.filter(ativo=True).prefetch_related('responsavel_aluno')

    return render(request, 'cad_aluno.html', {
        'aluno_form': aluno_form,
        'responsavel_form': responsavel_form,
        'alunos': alunos
    })


@login_required
@user_passes_test(is_diretoria)
def editar_aluno_responsavel(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    try:
        responsavel = Responsavel.objects.get(aluno=aluno)
    except Responsavel.DoesNotExist:
        responsavel = None

    if request.method == 'POST':
        aluno_form = AlunoForm(request.POST, instance=aluno)
        responsavel_form = ResponsavelForm(request.POST, instance=responsavel)

        if aluno_form.is_valid():
            # Salvar dados do aluno
            aluno = aluno_form.save(commit=False)

            # Atualizar usuário do aluno se necessário
            if not aluno.usuario and aluno.email:
                usuario_aluno, senha_aluno = criar_usuario_automatico(
                    aluno.email,
                    aluno.nome,
                    'Alunos'
                )
                if usuario_aluno:
                    aluno.usuario = usuario_aluno

            aluno.save()
            aluno_form.save_m2m()

            # Salvar dados do responsável
            if responsavel_form.is_valid():
                responsavel = responsavel_form.save(commit=False)
                responsavel.aluno = aluno

                # Atualizar usuário do responsável se necessário
                if not responsavel.usuario and responsavel.email:
                    usuario_responsavel, senha_responsavel = criar_usuario_automatico(
                        responsavel.email,
                        responsavel.nome,
                        'Responsaveis'
                    )
                    if usuario_responsavel:
                        responsavel.usuario = usuario_responsavel

                responsavel.save()

            messages.success(request, 'Aluno e responsável atualizados com sucesso!')
            return redirect('cad_aluno')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        aluno_form = AlunoForm(instance=aluno)
        responsavel_form = ResponsavelForm(instance=responsavel)

    return render(request, 'editar_aluno_responsavel.html', {
        'aluno_form': aluno_form,
        'responsavel_form': responsavel_form,
        'aluno': aluno,
        'responsavel': responsavel
    })


@login_required
@user_passes_test(is_diretoria)
def excluir_responsavel(request, responsavel_id):
    responsavel = get_object_or_404(Responsavel, id=responsavel_id)
    aluno_id = responsavel.aluno.id

    if request.method == 'POST':
        responsavel_nome = responsavel.nome
        responsavel.delete()
        messages.success(request, f'Responsável {responsavel_nome} excluído com sucesso!')

    return redirect('editar_aluno_responsavel', aluno_id=aluno_id)


@login_required
@user_passes_test(is_diretoria)
def cad_funcionarios(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            try:
                funcionario = form.save(commit=False)

                # Cria usuário automaticamente se não existir
                if not funcionario.usuario:
                    usuario, senha = criar_usuario_automatico(
                        funcionario.email,
                        funcionario.nome,
                        'Funcionarios'
                    )

                    if usuario:
                        funcionario.usuario = usuario
                        funcionario.save()

                        messages.success(
                            request,
                            f'Funcionário cadastrado com sucesso! '
                            f'Usuário: {usuario.username} | Senha: {senha}'
                        )
                    else:
                        funcionario.save()
                        messages.warning(
                            request,
                            'Funcionário cadastrado, mas não foi possível criar o usuário automático.'
                        )
                else:
                    funcionario.save()
                    messages.success(request, 'Funcionário atualizado com sucesso!')

                return redirect('cad_funcionarios')

            except Exception as e:
                messages.error(request, f'Erro ao cadastrar funcionário: {str(e)}')
    else:
        form = FuncionarioForm()

    funcionarios = Funcionario.objects.filter(ativo=True)
    return render(request, 'cad_funcionarios.html', {
        'form': form,
        'funcionarios': funcionarios
    })


# Views para gerenciamento de usuários
@login_required
@user_passes_test(is_diretoria)
def redefinir_senha_professor(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)

    if request.method == 'POST':
        if professor.usuario:
            nova_senha = gerar_senha_automatica()
            professor.usuario.set_password(nova_senha)
            professor.usuario.save()

            messages.success(
                request,
                f'Senha redefinida para o professor {professor.nome}. '
                f'Nova senha: {nova_senha}'
            )
        else:
            messages.error(request, 'Este professor não tem um usuário vinculado.')

    return redirect('cad_professor')


@login_required
@user_passes_test(is_diretoria)
def redefinir_senha_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    if request.method == 'POST':
        if aluno.usuario:
            nova_senha = gerar_senha_automatica()
            aluno.usuario.set_password(nova_senha)
            aluno.usuario.save()

            messages.success(
                request,
                f'Senha redefinida para o aluno {aluno.nome}. '
                f'Nova senha: {nova_senha}'
            )
        else:
            messages.error(request, 'Este aluno não tem um usuário vinculado.')

    return redirect('cad_aluno')


@login_required
@user_passes_test(is_diretoria)
def criar_usuario_manual_professor(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)

    if request.method == 'POST':
        if not professor.usuario:
            usuario, senha = criar_usuario_automatico(
                professor.email,
                professor.nome,
                'Professores'
            )

            if usuario:
                professor.usuario = usuario
                professor.save()
                messages.success(
                    request,
                    f'Usuário criado para o professor {professor.nome}. '
                    f'Usuário: {usuario.username} | Senha: {senha}'
                )
            else:
                messages.error(request, 'Não foi possível criar o usuário.')
        else:
            messages.warning(request, 'Este professor já tem um usuário vinculado.')

    return redirect('cad_professor')


@login_required
@user_passes_test(is_diretoria)
def criar_usuario_manual_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    if request.method == 'POST':
        if not aluno.usuario:
            usuario, senha = criar_usuario_automatico(
                aluno.email,
                aluno.nome,
                'Alunos'
            )

            if usuario:
                aluno.usuario = usuario
                aluno.save()
                messages.success(
                    request,
                    f'Usuário criado para o aluno {aluno.nome}. '
                    f'Usuário: {usuario.username} | Senha: {senha}'
                )
            else:
                messages.error(request, 'Não foi possível criar o usuário.')
        else:
            messages.warning(request, 'Este aluno já tem um usuário vinculado.')

    return redirect('cad_aluno')


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
        return redirect('login')


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