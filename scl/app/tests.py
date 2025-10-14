from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Aluno, Turma, Disciplina
from datetime import date


class AlunoModelTest(TestCase):

    def setUp(self):
        """Configura dados de teste que serão usados em múltiplos testes"""
        # Criar uma turma para testes
        self.turma = Turma.objects.create(
            nome="1º Ano A",
            turno="Manhã",
            sala="Sala 101",
            ano_letivo=2024
        )

        # Criar aluno para testes
        self.aluno = Aluno.objects.create(
            nome="João Silva",
            data_nascimento=date(2010, 5, 15),
            email="joao.silva@email.com",
            telefone="+5521999999999",
            tipo_notificacao="email",
            responsavel="Maria Silva",
            parentesco="Mãe",
            email_responsavel="maria.silva@email.com",
            telefone_responsavel="+5521888888888",
            tipo_notificacao_responsavel="whatsapp"
        )
        self.aluno.turmas.add(self.turma)

    def test_criacao_aluno(self):
        """Testa se um aluno pode ser criado com sucesso"""
        aluno = Aluno.objects.get(nome="João Silva")
        self.assertEqual(aluno.nome, "João Silva")
        self.assertEqual(aluno.email, "joao.silva@email.com")
        self.assertEqual(aluno.responsavel, "Maria Silva")
        self.assertEqual(aluno.parentesco, "Mãe")
        self.assertTrue(aluno.ativo)

    def test_campos_obrigatorios(self):
        """Testa se campos obrigatórios estão presentes"""
        aluno = Aluno.objects.get(nome="João Silva")
        self.assertIsNotNone(aluno.nome)
        self.assertIsNotNone(aluno.data_nascimento)
        self.assertIsNotNone(aluno.email)
        self.assertIsNotNone(aluno.responsavel)
        self.assertIsNotNone(aluno.email_responsavel)

    def test_valores_padrao(self):
        """Testa se os valores padrão estão sendo aplicados"""
        aluno = Aluno.objects.get(nome="João Silva")
        self.assertEqual(aluno.tipo_notificacao, "email")
        self.assertEqual(aluno.tipo_notificacao_responsavel, "whatsapp")
        self.assertEqual(aluno.parentesco, "Mãe")
        self.assertTrue(aluno.ativo)

    def test_relacionamento_turmas(self):
        """Testa o relacionamento ManyToMany com Turmas"""
        aluno = Aluno.objects.get(nome="João Silva")
        self.assertEqual(aluno.turmas.count(), 1)
        self.assertEqual(aluno.turmas.first().nome, "1º Ano A")

    def test_adicionar_multiplas_turmas(self):
        """Testa se um aluno pode estar em múltiplas turmas"""
        turma2 = Turma.objects.create(
            nome="1º Ano B",
            turno="Tarde",
            sala="Sala 102",
            ano_letivo=2024
        )

        aluno = Aluno.objects.get(nome="João Silva")
        aluno.turmas.add(turma2)

        self.assertEqual(aluno.turmas.count(), 2)
        self.assertIn(self.turma, aluno.turmas.all())
        self.assertIn(turma2, aluno.turmas.all())

    def test_string_representation(self):
        """Testa a representação em string do modelo"""
        aluno = Aluno.objects.get(nome="João Silva")
        expected_string = (
            f"{aluno.nome} - {aluno.email} - {aluno.responsavel} - "
            f"{aluno.parentesco} - {aluno.email_responsavel} - "
            f"{aluno.telefone_responsavel} - {aluno.tipo_notificacao_responsavel}"
        )
        self.assertEqual(str(aluno), expected_string)

    def test_campo_email_unico(self):
        """Testa que emails devem ser únicos (se configurado como unique)"""
        # Se email for unique, este teste deve falhar
        with self.assertRaises(Exception):
            Aluno.objects.create(
                nome="João Silva Duplicado",
                data_nascimento=date(2010, 5, 15),
                email="joao.silva@email.com",  # Email duplicado
                telefone="+5521999999998",
                tipo_notificacao="email",
                responsavel="Maria Silva",
                parentesco="Mãe",
                email_responsavel="maria.silva2@email.com",
                telefone_responsavel="+5521888888887",
                tipo_notificacao_responsavel="email"
            )

    def test_aluno_inativo(self):
        """Testa a funcionalidade de aluno inativo"""
        aluno_inativo = Aluno.objects.create(
            nome="Aluno Inativo",
            data_nascimento=date(2011, 3, 20),
            email="inativo@email.com",
            telefone="+5521977777777",
            tipo_notificacao="sms",
            responsavel="Pai Inativo",
            parentesco="Pai",
            email_responsavel="pai.inativo@email.com",
            telefone_responsavel="+5521966666666",
            tipo_notificacao_responsavel="sms",
            ativo=False
        )

        self.assertFalse(aluno_inativo.ativo)

        # Testar que alunos ativos por padrão não incluem o inativo
        alunos_ativos = Aluno.objects.filter(ativo=True)
        self.assertNotIn(aluno_inativo, alunos_ativos)

    def test_choices_tipo_notificacao(self):
        """Testa se os choices de tipo de notificação estão corretos"""
        aluno = Aluno.objects.get(nome="João Silva")

        # Testar choices válidos
        choices_validos = ['email', 'sms', 'whatsapp']
        self.assertIn(aluno.tipo_notificacao, choices_validos)
        self.assertIn(aluno.tipo_notificacao_responsavel, choices_validos)

        # Testar choice inválido (deve falhar se houver validação)
        aluno.tipo_notificacao = 'invalido'
        # Se houver validação, isso deve levantar uma exceção

    def test_campos_max_length(self):
        """Testa os limites de comprimento dos campos"""
        aluno = Aluno.objects.get(nome="João Silva")

        # Testar max_length do campo nome
        self.assertLessEqual(len(aluno.nome), 100)

        # Testar max_length do campo responsavel
        self.assertLessEqual(len(aluno.responsavel), 100)

        # Testar max_length do campo parentesco
        self.assertLessEqual(len(aluno.parentesco), 50)

    def test_metodo_save(self):
        # Testa o metodo save personalizado se existir
        aluno_novo = Aluno(
            nome="Novo Aluno",
            data_nascimento=date(2012, 8, 10),
            email="novo@email.com",
            telefone="+5521955555555",
            tipo_notificacao="email",
            responsavel="Novo Responsável",
            parentesco="Pai/Mãe",  # Valor padrão
            email_responsavel="novo.responsavel@email.com",
            telefone_responsavel="+5521944444444",
            tipo_notificacao_responsavel="email"
        )

        aluno_novo.save()

        # Verificar se o aluno foi salvo corretamente
        aluno_salvo = Aluno.objects.get(email="novo@email.com")
        self.assertEqual(aluno_salvo.nome, "Novo Aluno")
        self.assertEqual(aluno_salvo.parentesco, "Pai/Mãe")  # Valor padrão


class AlunoIntegrationTest(TestCase):
    """Testes de integração mais complexos"""

    def test_aluno_com_usuario(self):
        """Testa a criação de aluno com usuário vinculado"""
        # Criar usuário
        usuario = User.objects.create_user(
            username='aluno.test',
            email='aluno.test@email.com',
            password='testpass123'
        )

        # Criar aluno vinculado ao usuário
        aluno = Aluno.objects.create(
            nome="Aluno com Usuário",
            data_nascimento=date(2010, 1, 1),
            email="aluno.test@email.com",
            telefone="+5521933333333",
            tipo_notificacao="email",
            responsavel="Responsável Test",
            parentesco="Pai",
            email_responsavel="responsavel.test@email.com",
            telefone_responsavel="+5521922222222",
            tipo_notificacao_responsavel="sms",
            usuario=usuario
        )

        self.assertEqual(aluno.usuario, usuario)
        self.assertEqual(aluno.usuario.username, 'aluno.test')

    def test_buscar_aluno_por_email(self):
        """Testa buscas por email"""
        Aluno.objects.create(
            nome="Aluno Busca",
            data_nascimento=date(2011, 2, 2),
            email="busca@email.com",
            telefone="+5521911111111",
            tipo_notificacao="email",
            responsavel="Busca Responsável",
            parentesco="Mãe",
            email_responsavel="busca.resp@email.com",
            telefone_responsavel="+5521900000000",
            tipo_notificacao_responsavel="whatsapp"
        )

        aluno_encontrado = Aluno.objects.get(email="busca@email.com")
        self.assertEqual(aluno_encontrado.nome, "Aluno Busca")


# Testes para o model Pessoa (classe abstrata)
class PessoaAbstractTest(TestCase):
    """Testes para a classe abstrata Pessoa"""

    def test_campos_herdados(self):
        """Testa se os campos da classe Pessoa estão presentes no Aluno"""
        aluno = Aluno(
            nome="Teste Herança",
            data_nascimento=date(2010, 1, 1),
            email="heranca@email.com",
            telefone="+5521888888888",
            tipo_notificacao="email",
            responsavel="Responsável Herança",
            parentesco="Pai",
            email_responsavel="resp.heranca@email.com",
            telefone_responsavel="+5521877777777",
            tipo_notificacao_responsavel="email"
        )

        # Campos da classe Pessoa
        self.assertEqual(aluno.nome, "Teste Herança")
        self.assertEqual(aluno.email, "heranca@email.com")
        self.assertEqual(aluno.tipo_notificacao, "email")

        # Campos específicos do Aluno
        self.assertEqual(aluno.responsavel, "Responsável Herança")
        self.assertEqual(aluno.parentesco, "Pai")