from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.utils import timezone

somente_letras_unicode = RegexValidator(
    regex=r'^[^\W\d_]+(?:\s[^\W\d_]+)*$',
)


# Modelos Básicos
class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"


class Turma(models.Model):
    nome = models.CharField(max_length=100)
    disciplinas = models.ManyToManyField(Disciplina, blank=True, verbose_name="Disciplinas")
    turno = models.CharField(max_length=100)
    sala = models.CharField(max_length=100)
    ano_letivo = models.IntegerField(default=timezone.now().year)

    def __str__(self):
        return f"{self.nome} - {self.turno} - {self.sala}"

    def com_disciplinas(self):
        disciplinas_list = ", ".join([d.nome for d in self.disciplinas.all()])
        return f"{self.nome} - {disciplinas_list if disciplinas_list else 'Sem disciplinas'} - {self.turno} - {self.sala}"


# Modelos de Pessoas
class Pessoa(models.Model):
    TIPO_NOTIFICACAO_CHOICES = [
        ('email', 'E-mail'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    tipo_notificacao = models.CharField(max_length=10, choices=TIPO_NOTIFICACAO_CHOICES, verbose_name='Notificação', default='email')

    class Meta:
        abstract = True


class Professor(Pessoa):
    disciplinas = models.ManyToManyField(Disciplina, blank=True, verbose_name="Disciplinas")
    turmas = models.ManyToManyField(Turma, blank=True, verbose_name="Turmas")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.email}"

    def apenas_turmas(self):
        turmas_list = ", ".join([s.nome for s in self.turmas.all()])
        return f"{turmas_list}"


class Aluno(Pessoa):
    turmas = models.ManyToManyField(Turma, blank=True, verbose_name="Turma")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.email}"


class Responsavel(Pessoa):
    TIPO_NOTIFICACAO_CHOICES = [
        ('email', 'E-mail'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]

    aluno = models.OneToOneField(
        Aluno,
        on_delete=models.CASCADE,
        related_name='responsavel_aluno',
        verbose_name="Aluno"
    )
    parentesco = models.CharField(max_length=50, default="Pai/Mãe")
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF")

    def __str__(self):
        return f"{self.nome} - {self.parentesco} - {self.aluno.nome}"


class Funcionario(Pessoa):
    CARGO_CHOICES = [
        ('zelador', 'Zelador'),
        ('porteiro', 'Porteiro'),
        ('cantineiro', 'Cantineiro'),
        ('secretario', 'Secretário'),
    ]

    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.cargo}"


# Modelos Acadêmicos
class Aula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    data_aula = models.DateField()
    conteudo = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['turma', 'disciplina', 'data_aula']

    def __str__(self):
        return f"{self.disciplina} - {self.turma} - {self.data_aula}"


class Presenca(models.Model):
    SITUACAO_CHOICES = [
        ('presente', 'Presente'),
        ('falta', 'Falta'),
        ('falta_justificada', 'Falta Justificada'),
    ]

    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='presente')
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['aula', 'aluno']

    def __str__(self):
        return f"{self.aluno} - {self.aula} - {self.situacao}"


class TipoAvaliacao(models.Model):
    nome = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    def __str__(self):
        return f"{self.nome} (Peso: {self.peso})"


class Avaliacao(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    tipo_avaliacao = models.ForeignKey(TipoAvaliacao, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    data_avaliacao = models.DateField()
    valor_maximo = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.turma} - {self.data_avaliacao}"


class Nota(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    nota = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['avaliacao', 'aluno']

    def __str__(self):
        return f"{self.aluno} - {self.avaliacao}: {self.nota}"


# Modelos de Comunicação
class Aviso(models.Model):
    TIPO_AVISO_CHOICES = [
        ('geral', 'Geral'),
        ('nota', 'Lançamento de Nota'),
        ('falta', 'Falta'),
        ('falta_justificada', 'Falta Justificada'),
        ('evento', 'Evento'),
    ]

    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    tipo_aviso = models.CharField(max_length=20, choices=TIPO_AVISO_CHOICES)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField()
    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    destinatarios_turmas = models.ManyToManyField(Turma, blank=True)
    destinatarios_alunos = models.ManyToManyField(Aluno, blank=True)
    destinatarios_professores = models.ManyToManyField(Professor, blank=True)
    enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titulo} - {self.data_envio}"


# Modelos Financeiros
class ContaPagar(models.Model):
    CATEGORIA_CHOICES = [
        ('folha_pagamento', 'Folha de Pagamento'),
        ('agua', 'Água'),
        ('luz', 'Luz'),
        ('internet', 'Internet'),
        ('manutencao', 'Manutenção'),
        ('outros', 'Outros'),
    ]

    descricao = models.CharField(max_length=200)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    pago = models.BooleanField(default=False)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} - {self.data_vencimento}"


class ContaReceber(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_recebimento = models.DateField(null=True, blank=True)
    recebido = models.BooleanField(default=False)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.aluno} - {self.descricao} - R$ {self.valor}"


# Modelo específico para o SisProf
class SisProf(models.Model):
    # Este modelo pode ser usado para configurações gerais do sistema
    nome_escola = models.CharField(max_length=200, default="Nome da Escola")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    ano_letivo_atual = models.IntegerField(default=timezone.now().year)

    def __str__(self):
        return f"Sistema - {self.nome_escola}"