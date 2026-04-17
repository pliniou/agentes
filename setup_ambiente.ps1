param(
    [switch]$ForceInstall = $false
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Configuração de Ambiente dos Agentes   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar instalação do Python
Write-Host "[1/3] Verificando Python..."
if (-Not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "  -> Python não encontrado. Instalando via WinGet..." -ForegroundColor Yellow
    Try {
        winget install --id Python.Python.3.11 --exact --source winget --accept-package-agreements --accept-source-agreements
        Write-Host "  -> Python instalado. Por favor, feche e abra o terminal novamente após o fim do script para atualizar as variáveis de ambiente." -ForegroundColor Magenta
    } Catch {
        Write-Host "  -> Falha ao instalar Python. Instale manualmente: https://www.python.org/downloads/" -ForegroundColor Red
        Exit
    }
} else {
    $pythonVersion = python --version
    Write-Host "  -> OK! ($pythonVersion)" -ForegroundColor Green
}

# 2. Verificar instalação do pacote pip
Write-Host "[2/3] Verificando gerenciador de pacotes (pip)..."
if (-Not (Get-Command "pip" -ErrorAction SilentlyContinue)) {
    Write-Host "  -> pip não encontrado. Restaurando pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
    if ($?) {
        Write-Host "  -> pip restaurado com sucesso." -ForegroundColor Green
    } else {
        Write-Host "  -> Falha ao configurar o pip." -ForegroundColor Red
    }
} else {
    $pipVersion = pip --version
    Write-Host "  -> OK! ($pipVersion)" -ForegroundColor Green
}

# 3. Instalando as dependências do Projeto (Requirements)
Write-Host "[3/3] Checando dependências do projeto nos módulos Python..."

$requirementsFile = Join-Path -Path $PSScriptRoot -ChildPath "requirements.txt"

if (Test-Path $requirementsFile) {
    Write-Host "  -> Lendo e instalando pacotes de $requirementsFile" -ForegroundColor Yellow
    
    # Executa a instalação via pip (ele já pula automaticamente o que está instalado)
    python -m pip install -r $requirementsFile
    
    if ($?) {
        Write-Host "  -> OK! Dependências validadas e prontas." -ForegroundColor Green
    } else {
        Write-Host "  -> Erro ao instalar dependências. Verifique o pip." -ForegroundColor Red
    }
} else {
    Write-Host "  -> Arquivo requirements.txt não encontrado na pasta atual. Pulando instalação de pacotes Python..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Ambiente validado e pronto para uso!     " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
