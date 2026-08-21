"""
Tratamento de excecoes da API.

EXISTE POR CAUSA DO on_delete=PROTECT

Os models de dominio usam PROTECT nas chaves que apontam para AnaliseSolo,
para que apagar um cadastro auxiliar nunca leve o historico junto. So que o
DRF nao conhece ProtectedError: sem este arquivo a excecao sobe sem
tratamento e vira HTTP 500, com traceback no lugar de explicacao.

Um 500 aqui seria pior que o problema que o PROTECT resolve. O dado estaria
salvo, mas quem clicou em excluir veria "erro interno do servidor" e nao teria
como saber que o motivo foi um vinculo legitimo - nem quantos registros estao
no caminho.

Este manipulador converte a recusa do banco em 409 Conflict com uma mensagem
que nomeia o que esta bloqueando e quantos sao. 409 e o codigo certo: o pedido
esta correto, mas conflita com o estado atual do recurso.
"""
from collections import Counter

from django.db.models import ProtectedError, RestrictedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _descrever(objetos):
    """
    Devolve (texto, total) - por exemplo ('17 análises de solo', 17).

    Agrupa por model e usa o verbose_name declarado, para a mensagem sair na
    linguagem do dominio em vez de nomes de classe. O total sai junto porque
    quem monta a frase precisa dele para concordar o verbo.
    """
    contagem = Counter(tipo._meta for tipo in objetos)

    partes = []
    total = 0
    for meta, quantidade in contagem.most_common():
        total += quantidade
        nome = meta.verbose_name if quantidade == 1 else meta.verbose_name_plural
        partes.append(f'{quantidade} {nome}'.lower())

    if not partes:
        return 'registros vinculados', 2
    if len(partes) == 1:
        return partes[0], total
    return ', '.join(partes[:-1]) + f' e {partes[-1]}', total


def manipulador_de_excecoes(exc, context):
    """
    Manipulador padrao do DRF (config/settings.py, REST_FRAMEWORK).

    Trata o que o DRF nao trata e delega o resto.
    """
    if isinstance(exc, (ProtectedError, RestrictedError)):
        # 'protected_objects' e 'restricted_objects' guardam os registros que
        # impediram a exclusao - e o que permite dizer quantos sao.
        bloqueando = getattr(exc, 'protected_objects', None)
        if bloqueando is None:
            bloqueando = getattr(exc, 'restricted_objects', [])

        texto, total = _descrever(bloqueando)
        verbo = 'depende' if total == 1 else 'dependem'
        instrucao = (
            'Exclua ou reatribua esse registro primeiro.' if total == 1
            else 'Exclua ou reatribua esses registros primeiro.'
        )

        return Response(
            {'detail': f'Não é possível excluir: {texto} {verbo} deste registro. {instrucao}'},
            status=status.HTTP_409_CONFLICT,
        )

    return exception_handler(exc, context)
