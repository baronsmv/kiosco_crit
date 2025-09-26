@echo off
setlocal

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

set sessionPath=whatsapp_node\sessions\session

if exist "%sessionPath%\SingletonLock" del "%sessionPath%\SingletonLock"
if exist "%sessionPath%\SingletonCookie" del "%sessionPath%\SingletonCookie"
if exist "%sessionPath%\SingletonSocket" del "%sessionPath%\SingletonSocket"

echo [INFO] Deteniendo contenedores previos (si existen)...
docker compose down

echo [INFO] Levantando servicios Docker...
docker compose up --build

pause
