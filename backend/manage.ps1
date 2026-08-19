# Atalho para rodar o manage.py sem virtualenv.
#
# POR QUE ISTO EXISTE
# O Smart App Control do Windows bloqueia a copia do python.exe que o modulo
# 'venv' cria dentro de venv/Scripts/. O bloqueio vale em qualquer pasta, e o
# Smart App Control nao aceita excecao por arquivo: so pode ser desligado por
# inteiro, e uma vez desligado nao pode ser religado sem reinstalar o Windows.
#
# A alternativa aqui evita o problema pela raiz: as dependencias vao para a
# pasta 'libs/' (pip install --target) e o interpretador do sistema e usado
# direto, sem copia nenhuma. O isolamento por projeto se mantem.
#
# USO
#   .\manage.ps1 runserver
#   .\manage.ps1 migrate
#   .\manage.ps1 createsuperuser
#
# SE UM DIA O VENV VOLTAR A FUNCIONAR
# (ligando o Modo Desenvolvedor e usando 'python -m venv --symlinks venv',
# ou desligando o Smart App Control), este arquivo pode ser apagado e o fluxo
# normal com 'venv\Scripts\Activate.ps1' volta a valer.

$ErrorActionPreference = 'Stop'

$libs = Join-Path $PSScriptRoot 'libs'

if (-not (Test-Path $libs)) {
    Write-Host "A pasta 'libs/' nao existe. Instalando as dependencias..." -ForegroundColor Yellow
    & py -3.12 -m pip install --target $libs -r (Join-Path $PSScriptRoot 'requirements.txt')
}

$env:PYTHONPATH = $libs
& py -3.12 (Join-Path $PSScriptRoot 'manage.py') @args
