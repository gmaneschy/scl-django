from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

somente_letras_unicode = RegexValidator(
    regex=r'^[^\W\d_]+(?:\s[^\W\d_]+)*$',
)


# Create your models here.
class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.nome}"

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    disciplinas = models.ManyToManyField(Disciplina, blank=True, verbose_name="Disciplinas")
    turno = models.CharField(max_length=100)
    sala = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} - {self.turno} - {self.sala}"

    def com_disciplinas(self):
        """Metodo específico para quando quiser mostrar com disciplinas"""
        disciplinas_list = ", ".join([d.nome for d in self.disciplinas.all()])
        return f"{self.nome} - {disciplinas_list if disciplinas_list else 'Sem disciplinas'} - {self.turno} - {self.sala}"

class Professor(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField()
    disciplinas = models.ManyToManyField(Disciplina, blank=True, verbose_name="Disciplinas")
    turmas = models.ManyToManyField(Turma, blank=True, verbose_name="Turma")

    def __str__(self):
        disciplinas_list = ", ".join([d.nome for d in self.disciplinas.all()])
        return (f"{self.nome} - {self.data_nascimento} - {self.email} - {self.telefone} "
                f"- {disciplinas_list if disciplinas_list else 'Sem disciplinas'} - {self.turmas}")

    def apenas_turmas(self):
        turmas_list = ", ".join([s.nome for s in self.turmas.all()])
        return f"{turmas_list}"

class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField()
    turmas = models.ManyToManyField(Turma, blank=True, verbose_name="Turma")

    r_nome = models.CharField(max_length=100, verbose_name="Nome do Responsável")
    r_email = models.EmailField(verbose_name="E-mail do Responsável")
    r_telefone = models.CharField(verbose_name="Telefone do Responsável")
    def __str__(self):
        return (f"{self.nome} - {self.data_nascimento} - {self.email} "
                f"- {self.telefone} - {self.turmas}"
                f"- {self.r_nome} - {self.r_email} - {self.r_telefone}")

class SisProf(models.Model):
    pass