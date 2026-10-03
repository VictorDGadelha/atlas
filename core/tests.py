from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Atividade, AtividadeDia, Refeicao, RegistroPeso

User = get_user_model()


class BaseTest(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('usuario', password='senha-teste-123')
        self.outro = User.objects.create_user('outro', password='senha-teste-123')
        self.client.login(username='usuario', password='senha-teste-123')
        self.hoje = timezone.localdate()


class AutenticacaoTests(BaseTest):
    def test_paginas_exigem_login(self):
        self.client.logout()
        for nome in ['home', 'peso', 'alimentacao', 'checklist', 'historico']:
            resposta = self.client.get(reverse(nome))
            self.assertRedirects(resposta, f"{reverse('login')}?next={reverse(nome)}")


class PesoTests(BaseTest):
    def test_mesma_data_atualiza_em_vez_de_duplicar(self):
        dados = {'data': self.hoje.isoformat(), 'peso': '72.5'}
        self.client.post(reverse('peso'), dados)
        dados['peso'] = '71.9'
        self.client.post(reverse('peso'), dados)

        registros = RegistroPeso.objects.filter(usuario=self.usuario)
        self.assertEqual(registros.count(), 1)
        self.assertEqual(registros.get().peso, Decimal('71.9'))

    def test_rejeita_data_futura(self):
        amanha = self.hoje + timedelta(days=1)
        self.client.post(reverse('peso'), {'data': amanha.isoformat(), 'peso': '70'})
        self.assertEqual(RegistroPeso.objects.count(), 0)

    def test_rejeita_peso_fora_da_faixa(self):
        self.client.post(reverse('peso'), {'data': self.hoje.isoformat(), 'peso': '5'})
        self.assertEqual(RegistroPeso.objects.count(), 0)

    def test_nao_exclui_registro_de_outro_usuario(self):
        registro = RegistroPeso.objects.create(
            usuario=self.outro, data=self.hoje, peso=Decimal('80')
        )
        resposta = self.client.post(reverse('peso_excluir', args=[registro.pk]))
        self.assertEqual(resposta.status_code, 404)
        self.assertTrue(RegistroPeso.objects.filter(pk=registro.pk).exists())


class AlimentacaoTests(BaseTest):
    def test_total_soma_apenas_calorias_do_usuario_no_dia(self):
        Refeicao.objects.create(usuario=self.usuario, data=self.hoje, tipo='cafe',
                                descricao='Pão', calorias=300)
        Refeicao.objects.create(usuario=self.usuario, data=self.hoje, tipo='almoco',
                                descricao='Arroz', calorias=600)
        Refeicao.objects.create(usuario=self.usuario, data=self.hoje, tipo='lanche',
                                descricao='Fruta')
        Refeicao.objects.create(usuario=self.outro, data=self.hoje, tipo='jantar',
                                descricao='Outro usuário', calorias=999)

        resposta = self.client.get(reverse('alimentacao'))
        self.assertEqual(resposta.context['total_calorias'], 900)
        self.assertEqual(resposta.context['refeicoes'].count(), 3)


class ChecklistTests(BaseTest):
    def test_gera_lista_do_dia(self):
        Atividade.objects.create(usuario=self.usuario, nome='Caminhar')
        self.client.get(reverse('checklist'))
        self.assertTrue(
            AtividadeDia.objects.filter(atividade__nome='Caminhar', data=self.hoje).exists()
        )

    def test_atividade_nova_nao_aparece_em_dias_anteriores(self):
        Atividade.objects.create(usuario=self.usuario, nome='Caminhar')
        ontem = self.hoje - timedelta(days=1)
        resposta = self.client.get(reverse('checklist'), {'data': ontem.isoformat()})
        self.assertEqual(resposta.context['itens'].count(), 0)

    def test_marcar_salva_e_retorna_resumo(self):
        atividade = Atividade.objects.create(usuario=self.usuario, nome='Caminhar')
        item = AtividadeDia.objects.create(atividade=atividade, data=self.hoje)

        resposta = self.client.post(reverse('checklist_marcar', args=[item.pk]),
                                    {'concluida': 'true'})
        item.refresh_from_db()

        self.assertTrue(item.concluida)
        self.assertEqual(resposta.json()['percentual'], 100)

    def test_nao_marca_item_de_outro_usuario(self):
        atividade = Atividade.objects.create(usuario=self.outro, nome='Estudar')
        item = AtividadeDia.objects.create(atividade=atividade, data=self.hoje)

        resposta = self.client.post(reverse('checklist_marcar', args=[item.pk]),
                                    {'concluida': 'true'})
        item.refresh_from_db()

        self.assertEqual(resposta.status_code, 404)
        self.assertFalse(item.concluida)

    def test_nome_duplicado_e_rejeitado(self):
        self.client.post(reverse('atividade_criar'), {'nome': 'Beber água'})
        self.client.post(reverse('atividade_criar'), {'nome': 'beber água'})
        self.assertEqual(Atividade.objects.filter(usuario=self.usuario).count(), 1)


class HistoricoTests(BaseTest):
    def test_periodo_invalido_cai_no_padrao(self):
        for valor in ['abc', '999']:
            resposta = self.client.get(reverse('historico'), {'periodo': valor})
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.context['periodo'], 30)