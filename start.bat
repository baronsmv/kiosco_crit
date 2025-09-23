@echo off
setlocal

set interface="Ethernet"

netsh interface ip set address name=%interface% static 10.7.20.23 255.255.255.0 10.7.20.1
netsh interface ip set dns name=%interface% static 8.8.8.8
netsh interface ip add dns name=%interface% 8.8.4.4 index=2

echo Network settings updated.

echo [INFO] Verificando si Docker está corriendo...
docker info >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo [INFO] Docker no está corriendo. Iniciando Docker Desktop...
    start "" /min "C:\Program Files\Docker\Docker\Docker Desktop.exe"

    echo [INFO] Esperando que Docker inicie...
    :wait_docker
    timeout /t 2 >nul
    docker info >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        goto wait_docker
    )
    echo [INFO] Docker está listo.
) else (
    echo [INFO] Docker ya está en ejecución.
)

echo [INFO] Levantando servicios Docker...
start "Docker Compose" cmd /k docker compose up --build
