"""
Gera as duas variantes da imagem de fundo a partir de uma foto de origem.

    python scripts/gerar-fundo.py "../backend/analise solo.jpg"

Sai em src/assets/:

    solo.webp          telas internas — desfocada, 900px
    solo-nitido.webp   login          — nitida, tamanho nativo

POR QUE DUAS

Nas telas internas o titulo fica direto sobre o fundo, entao a imagem entra
desfocada: o desfoque apaga a alta frequencia (o grao do solo, as letras dos
hexagonos) que atrapalha ler texto por cima. No login nao ha texto sobre o
fundo — o cartao e opaco — entao a foto aparece inteira.

Efeito colateral util: desfoque destroi detalhe, e detalhe e o que ocupa bytes.
A variante desfocada cabe em ~6 KB, pequena o bastante para o webpack embutir
como data URI no CSS, o que elimina uma requisicao.

As imagens vao para src/assets/ e NAO para public/. O base.css passa pelo
webpack, e ali um url('/img/...') e tratado como caminho de modulo, nao como
URL: o build quebra com 'Cannot find module'.

Requer Pillow:  pip install Pillow
"""
import os
import sys

from PIL import Image, ImageFilter

# Onde as imagens precisam cair para o base.css encontra-las.
DESTINO = os.path.join(os.path.dirname(__file__), '..', 'src', 'assets')

# Raio do desfoque, em pixels sobre a imagem de origem. Abaixo de ~6 o grao do
# solo ainda aparece atras do titulo das telas.
RAIO_DESFOQUE = 9

# A desfocada nao precisa de resolucao: o desfoque ja apagou o detalhe.
LARGURA_SUAVE = 900

# 62 mantem o arquivo abaixo do JPEG de origem. Como a imagem e so fundo e
# ainda passa por um veu, artefato de compressao nao aparece.
QUALIDADE_NITIDA = 62
QUALIDADE_SUAVE = 70


def gerar(origem):
    base = Image.open(origem).convert('RGB')
    os.makedirs(DESTINO, exist_ok=True)

    altura = round(LARGURA_SUAVE * base.size[1] / base.size[0])
    suave = base.filter(ImageFilter.GaussianBlur(RAIO_DESFOQUE))
    suave = suave.resize((LARGURA_SUAVE, altura), Image.LANCZOS)
    suave.save(os.path.join(DESTINO, 'solo.webp'), 'WEBP',
               quality=QUALIDADE_SUAVE, method=6)

    # Sem redimensionar: ampliar nao acrescenta informacao, so peso.
    base.save(os.path.join(DESTINO, 'solo-nitido.webp'), 'WEBP',
              quality=QUALIDADE_NITIDA, method=6)

    for nome in ('solo.webp', 'solo-nitido.webp'):
        caminho = os.path.join(DESTINO, nome)
        im = Image.open(caminho)
        print(f'{nome:18s} {im.size[0]}x{im.size[1]:<5d} '
              f'{os.path.getsize(caminho) / 1024:6.1f} KB')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    gerar(sys.argv[1])
