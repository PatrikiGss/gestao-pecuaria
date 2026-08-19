import django_filters

from .models import AnaliseSolo, Recomendacao


class AnaliseSoloFilter(django_filters.FilterSet):
    """
    Filtros da listagem de analises.

    Com o historico paginado, o cliente precisa conseguir chegar direto ao
    que procura em vez de percorrer pagina por pagina. 'propriedade' atravessa
    a gleba, ja que a analise nao guarda mais esse vinculo diretamente.
    """

    propriedade = django_filters.NumberFilter(field_name='gleba__propriedade')
    data_apos = django_filters.DateFilter(field_name='data', lookup_expr='gte')
    data_antes = django_filters.DateFilter(field_name='data', lookup_expr='lte')

    class Meta:
        model = AnaliseSolo
        fields = ['propriedade', 'gleba', 'cultura', 'laboratorio']


class RecomendacaoFilter(django_filters.FilterSet):
    propriedade = django_filters.NumberFilter(
        field_name='analise_solo__gleba__propriedade'
    )
    gleba = django_filters.NumberFilter(field_name='analise_solo__gleba')

    class Meta:
        model = Recomendacao
        fields = ['analise_solo', 'propriedade', 'gleba']
