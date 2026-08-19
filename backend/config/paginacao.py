from rest_framework.pagination import PageNumberPagination


class PaginacaoPadrao(PageNumberPagination):
    """
    Paginacao aplicada a todas as listagens da API.

    Antes as listagens devolviam a colecao inteira a cada requisicao. O
    historico de analises cresce indefinidamente, entao o custo aumentava com
    o tempo de uso - justamente para o cliente mais antigo, que tem mais dados.

    A resposta passa a ter a forma:
        {"count": 137, "next": "...?page=2", "previous": null, "results": [...]}

    'page_size' permite ao cliente pedir mais itens numa tacada, ate o teto de
    max_page_size. E o que as telas usam para preencher listas suspensas de
    cadastro, que sao curtas e precisam vir completas.
    """

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200
