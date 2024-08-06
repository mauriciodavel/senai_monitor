# Seu script original começa aqui
try {
    # Certifique-se de executar este script como Administrador

    # Verifique se o Python já está instalado
    $python = Get-Command python -ErrorAction SilentlyContinue

    if ($python) {
        Write-Output "Python já está instalado. Pulando a instalação do Python..."
    } else {
        # Defina o caminho do arquivo de instalação do Python
        $pythonInstaller = "$PSScriptRoot\python-3.12.4-amd64.exe"

        # Verifique se o arquivo de instalação do Python existe
        if (-Not (Test-Path $pythonInstaller)) {
            Write-Error "Arquivo de instalação do Python não encontrado. Certifique-se de que o arquivo 'python-3.12.4-amd64.exe' está na mesma pasta que este script."
            exit 1
        }

        # Instale o Python
        Write-Output "Instalando o Python..."
        Start-Process -Wait -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1"

        # Verifique se o Python foi instalado corretamente
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) {
            Write-Error "Falha na instalação do Python. O script será encerrado."
            exit 1
        }
    }

    # Função para verificar se uma biblioteca Python está instalada
    function Test-PythonModule {
        param (
            [string]$moduleName
        )
        $check = python -c "import $moduleName" 2>&1
        return -not ($check -match "ModuleNotFoundError")
    }

    # Verifique e instale as bibliotecas necessárias
    $libraries = @("mysql-connector-python", "pandas", "matplotlib", "tk")

    foreach ($lib in $libraries) {
        if (Test-PythonModule -moduleName $lib) {
            Write-Output "$lib já está instalado."
        } else {
            Write-Output "Instalando $lib..."
            python -m pip install $lib
        }
    }

    # Crie a pasta "C:\Program Files\Senai Monitor"
    $installPath = "C:\Program Files\Senai Monitor"
    if (-Not (Test-Path $installPath)) {
        Write-Output "Criando a pasta $installPath..."
        New-Item -ItemType Directory -Path $installPath
    }

    # Copie o executável para a pasta de destino
    $exePath = "$PSScriptRoot\coleta_dados_3.exe"
    if (-Not (Test-Path $exePath)) {
        Write-Error "Arquivo executável 'coleta_dados_3.exe' não encontrado na pasta de origem."
        exit 1
    }

    Write-Output "Copiando o arquivo executável para $installPath..."
    Copy-Item -Path $exePath -Destination $installPath

    # Crie um atalho para o executável na pasta de inicialização
    $shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\coleta_dados_3.lnk"
    $targetPath = "$installPath\coleta_dados_3.exe"

    Write-Output "Criando atalho para o executável na pasta de inicialização..."
    $WScriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $targetPath
    $shortcut.Save()

    # Execute o arquivo executável em segundo plano e exiba a mensagem de sucesso ou erro
    try {
        Write-Output "Iniciando o monitoramento..."
        Start-Process -FilePath $targetPath -NoNewWindow
        Write-Output "Monitoramento inicializado com sucesso."
    } catch {
        Write-Error "Erro ao iniciar o monitoramento: $_"
    }
} finally {
    # Não é necessário restaurar a política de execução, pois ela é temporária para o processo
    Write-Output "Script concluído."
}
