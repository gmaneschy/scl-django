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
        disciplinas_list = ", ".join([d.nome for d in self.disciplinas.all()])
        return f"{self.nome} - {disciplinas_list if disciplinas_list else 'Sem disciplinas'} - {self.turno} - {self.sala}"


class Professor(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField()
    disciplinas = models.ManyToManyField(Disciplina, blank=True, verbose_name="Disciplinas")
    def __str__(self):
        disciplinas_list = ", ".join([d.nome for d in self.disciplinas.all()])
        return (f"{self.nome} - {self.data_nascimento} - {self.email} - {self.telefone} "
                f"- {disciplinas_list if disciplinas_list else 'Sem disciplinas'}")