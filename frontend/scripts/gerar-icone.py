"""
Gera o icone do Projeto AORUS (aba do navegador e app instalado).

    python scripts/gerar-icone.py

Sai em public/favicon.ico e public/img/icons/.

O DESENHO

Um broto de duas folhas sobre uma faixa de terra, em verde claro sobre o
verde escuro da paleta (--cor-barra). Escolhido por conversar com o que o
sistema faz - analise de solo para decidir correcao e adubacao - e com a
foto de fundo, que e mao, muda e terra.

POR QUE E TAO SIMPLES

O favicon e visto a 16 pixels. Nesse tamanho, detalhe vira sujeira: contorno
fino some, gradiente vira borrao, e qualquer coisa alem de duas ou tres formas
solidas deixa de ser reconhecivel. O desenho e feito grande (512px) e reduzido
com LANCZOS, mas so sobrevive a reducao porque as formas sao poucas, grandes e
de alto contraste.

Requer Pillow:  pip install Pillow
"""
import os

from PIL import Image, ImageDraw

AQUI = os.path.dirname(__file__)
PUBLICO = os.path.join(AQUI, '..', 'public')

# Cores da paleta (src/estilos/base.css).
FUNDO = (20, 64, 31)        # --cor-barra
BROTO = (140, 214, 160)     # verde claro, legivel sobre o fundo
TERRA = (94, 71, 47)        # faixa de solo

LADO = 512

# Tamanhos que entram no .ico. O navegador escolhe conforme o contexto:
# 16 na aba, 32 na barra de favoritos, 48 no atalho da area de trabalho.
TAMANHOS_ICO = [16, 24, 32, 48, 64, 128, 256]


def folha(imagem, centro, comprimento, largura, angulo):
    """
    Uma folha: elipse deitada, girada, e colada sobre a imagem.

    O giro exige uma camada propria - o Pillow nao gira uma forma isolada.
    A camada e do tamanho da imagem toda para o centro de rotacao coincidir
    com o ponto pedido, sem conta de deslocamento.
    """
    camada = Image.new('RGBA', imagem.size, (0, 0, 0, 0))
    cx, cy = centro
    ImageDraw.Draw(camada).ellipse(
        [cx - comprimento / 2, cy - largura / 2,
         cx + comprimento / 2, cy + largura / 2],
        fill=BROTO,
    )
    girada = camada.rotate(angulo, resample=Image.BICUBIC, center=centro)
    imagem.alpha_composite(girada)


def desenhar():
    imagem = Image.new('RGBA', (LADO, LADO), (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)

    # Fundo: quadrado de cantos arredondados. Preenche a area toda, para o
    # icone nao encolher visualmente ao lado dos vizinhos na barra de abas.
    desenho.rounded_rectangle([0, 0, LADO, LADO], radius=int(LADO * 0.22), fill=FUNDO)

    # Faixa de terra, encostada na base. E ela que faz o broto ser um broto e
    # nao um trevo solto: da chao, e diz do que o sistema trata.
    # Vai ate a borda inferior e e recortada pela mascara do quadrado
    # arredondado: assim vira CHAO, e nao uma barra flutuando no meio.
    topo_terra = int(LADO * 0.74)
    terra = Image.new('RGBA', (LADO, LADO), (0, 0, 0, 0))
    ImageDraw.Draw(terra).rectangle([0, topo_terra, LADO, LADO], fill=TERRA)
    mascara = Image.new('L', (LADO, LADO), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [0, 0, LADO, LADO], radius=int(LADO * 0.22), fill=255)
    imagem.paste(terra, (0, 0), Image.composite(
        mascara, Image.new('L', (LADO, LADO), 0), terra.split()[3]))

    # Caule: nasce DENTRO da terra e sobe ate onde as folhas se encontram.
    # Comecar abaixo do topo da faixa evita a emenda visivel que aparece
    # quando as duas formas apenas se tocam.
    largura_caule = int(LADO * 0.085)
    desenho.rounded_rectangle(
        [LADO // 2 - largura_caule // 2, int(LADO * 0.30),
         LADO // 2 + largura_caule // 2, topo_terra + int(LADO * 0.04)],
        radius=largura_caule // 2, fill=BROTO,
    )

    # Duas folhas simetricas, inclinadas para cima. O centro de cada uma fica
    # deslocado do caule por pouco menos da metade do comprimento, entao a
    # ponta interna ENTRA no caule - sem essa sobreposicao as folhas flutuam
    # soltas. O deslocamento e calibrado para elas se encostarem no caule mas
    # NAO uma na outra: o entalhe em V no topo e o que faz ler 'duas folhas'
    # em vez de uma mancha unica quando o icone encolhe para 16px.
    comprimento = LADO * 0.40
    largura = LADO * 0.21
    altura_folhas = int(LADO * 0.36)
    for angulo, lado in ((38, -1), (-38, 1)):
        centro = (LADO / 2 + lado * comprimento * 0.47, altura_folhas)
        folha(imagem, centro, comprimento, largura, angulo)

    return imagem


# Mesma geometria do desenho acima, em vetor. Os numeros saem das mesmas
# proporcoes; se uma mudar la, mude aqui.
SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <clipPath id="quadro">
      <rect width="512" height="512" rx="113"/>
    </clipPath>
  </defs>
  <g clip-path="url(#quadro)">
    <rect width="512" height="512" fill="{fundo}"/>
    <rect y="379" width="512" height="133" fill="{terra}"/>
    <rect x="235" y="154" width="43" height="246" rx="21" fill="{broto}"/>
    <ellipse cx="160" cy="184" rx="102" ry="54" fill="{broto}"
             transform="rotate(-38 160 184)"/>
    <ellipse cx="352" cy="184" rx="102" ry="54" fill="{broto}"
             transform="rotate(38 352 184)"/>
  </g>
</svg>
'''

# Icone de aba fixada do Safari: silhueta de uma cor so, sem fundo - o
# navegador aplica a cor dele por cima, entao aqui vai preto chapado.
SVG_MASCARA = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect x="235" y="154" width="43" height="246" rx="21"/>
  <ellipse cx="160" cy="184" rx="102" ry="54" transform="rotate(-38 160 184)"/>
  <ellipse cx="352" cy="184" rx="102" ry="54" transform="rotate(38 352 184)"/>
</svg>
'''


def cor(rgb):
    return '#%02x%02x%02x' % rgb


def main():
    base = desenhar()

    caminho_ico = os.path.abspath(os.path.join(PUBLICO, 'favicon.ico'))
    base.save(caminho_ico, format='ICO',
              sizes=[(t, t) for t in TAMANHOS_ICO])
    print('%-46s %6.1f KB' % (caminho_ico, os.path.getsize(caminho_ico) / 1024))

    # Conjunto do PWA: sem isto o app instalado continuaria com o icone do
    # scaffold do Vue, enquanto a aba ja mostraria o novo.
    icones = os.path.abspath(os.path.join(PUBLICO, 'img', 'icons'))
    os.makedirs(icones, exist_ok=True)
    for nome, tamanho in [
        ('favicon-16x16.png', 16), ('favicon-32x32.png', 32),
        ('apple-touch-icon-60x60.png', 60), ('apple-touch-icon-76x76.png', 76),
        ('apple-touch-icon-120x120.png', 120), ('apple-touch-icon-152x152.png', 152),
        ('apple-touch-icon-180x180.png', 180), ('apple-touch-icon.png', 180),
        ('android-chrome-192x192.png', 192), ('android-chrome-512x512.png', 512),
        ('android-chrome-maskable-192x192.png', 192),
        ('android-chrome-maskable-512x512.png', 512),
        ('msapplication-icon-144x144.png', 144), ('mstile-150x150.png', 150),
    ]:
        base.resize((tamanho, tamanho), Image.LANCZOS).save(
            os.path.join(icones, nome), format='PNG')
    print('%-46s %d arquivos' % (icones, 14))

    # O plugin de PWA injeta <link rel="icon" href="/img/icons/favicon.svg">,
    # mas o scaffold nunca criou esse arquivo: eram 404 em toda visita, com o
    # navegador caindo nos PNG. Em vetor o icone fica nitido em qualquer
    # tamanho e em qualquer densidade de tela.
    with open(os.path.join(icones, 'favicon.svg'), 'w', encoding='utf-8') as f:
        f.write(SVG.format(fundo=cor(FUNDO), terra=cor(TERRA), broto=cor(BROTO)))
    with open(os.path.join(icones, 'safari-pinned-tab.svg'), 'w', encoding='utf-8') as f:
        f.write(SVG_MASCARA)
    print('%-46s %s' % (icones, 'favicon.svg e safari-pinned-tab.svg'))


if __name__ == '__main__':
    main()
