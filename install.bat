@echo off

set BLENDER_VERSION=4.5.10
set BLENDER_SHORT_VERSION=4.5
set BLENDER_URL=https://download.blender.org/release/Blender%BLENDER_SHORT_VERSION%/blender-%BLENDER_VERSION%-windows-x64.zip

set HIDAPI_VERSION=0.15.0
set HIDAPI_URL=https://github.com/libusb/hidapi/releases/download/hidapi-%HIDAPI_VERSION%/hidapi-win.zip

set ADDONS_BUNDLE_URL=https://github.com/bertoramos/blender-editor/releases/download/v1.11.1/robotcontrol-toolbox-blender4.2.9LTS-v1.11.1.zip

set TARGET_ARCH=x64


set AUTOINSTALL_DIR=%~dp0
cd %AUTOINSTALL_DIR%
:: ***************************
:: **** DESCARGAR BLENDER ****
:: ***************************

:: --- PASO 1: DESCARGAR ---
curl -L -o blender.zip "%BLENDER_URL%"

:: --- PASO 2: EXTRAER ---
tar -xf blender.zip
del blender.zip

:: --- PASO 3: CREAR CARPETA portable ---
MKDIR .\blender-%BLENDER_VERSION%-windows-x64\portable\

:: --- PASO 4: ACTIVAR INTERNET PERMANENTEMENTE Y MEASUREIT ---
cd .\blender-%BLENDER_VERSION%-windows-x64\

:: 1. Habilitar Allow Online Access permanentemente en preferencias (sin interfaz)
blender.exe -b --python-expr "import bpy; bpy.context.preferences.system.use_online_access = True; bpy.ops.wm.save_userpref()"

:: 2. Agregar repositorio oficial de Blender (sin interfaz)
blender.exe -b --online-mode --command extension repo-add blender_org --name "Blender" --url https://extensions.blender.org/api/v1/extensions/

:: 3. Sincronizar repositorios (sin interfaz)
blender.exe -b --online-mode --command extension sync

:: 4. Instalar y activar Measureit con acceso online (sin interfaz)
blender.exe -b --online-mode --command extension install -e measureit

:: --- PASO 5: INSTALAR DEPENDENCIAS PYTHON ---
cd .\%BLENDER_SHORT_VERSION%\python\bin\
.\python.exe -m ensurepip
.\python.exe -m pip install --upgrade pip
.\python.exe -m pip install -r %AUTOINSTALL_DIR%\requirements.txt

:: --- PASO 6: DESCARGAR dll hidapi ---
curl -L -o hidapi-win.zip %HIDAPI_URL%

mkdir hidapi-temp
tar -xf hidapi-win.zip -C hidapi-temp
copy hidapi-temp\%TARGET_ARCH%\hidapi.dll %AUTOINSTALL_DIR%blender-%BLENDER_VERSION%-windows-%TARGET_ARCH%\hidapi.dll
copy hidapi-temp\%TARGET_ARCH%\hidapi.dll %AUTOINSTALL_DIR%blender-%BLENDER_VERSION%-windows-%TARGET_ARCH%\%BLENDER_SHORT_VERSION%\python\bin\hidapi.dll
rmdir /s /q hidapi-temp
del hidapi-win.zip

:: retornar carpeta base
cd %AUTOINSTALL_DIR%

:: --- PASO 7: DESCARGAR ADDONS DEL PROYECTO ---
set ADDONS_OK=1
for %%A in (archibuilder.zip filemanager.zip robotcontrol.zip utilities.zip) do (
    if not exist ".\%%A" set ADDONS_OK=0
)

if %ADDONS_OK%==0 (
    echo Faltan addons. Descargando paquete completo...
    curl -L -o addons-bundle.zip "%ADDONS_BUNDLE_URL%"
    mkdir addons-temp
    tar -xf addons-bundle.zip -C addons-temp
    copy /Y addons-temp\archibuilder.zip .\
    copy /Y addons-temp\filemanager.zip .\
    copy /Y addons-temp\robotcontrol.zip .\
    copy /Y addons-temp\utilities.zip .\
    rmdir /s /q addons-temp
    del addons-bundle.zip
) else (
    echo Todos los addons ya estan presentes.
)

:: --- PASO 8: INSTALAR ADDONS EN BLENDER ---
set ADDONS_DIR=%AUTOINSTALL_DIR%blender-%BLENDER_VERSION%-windows-%TARGET_ARCH%\portable\scripts\addons
mkdir "%ADDONS_DIR%" 2>nul
for %%A in (archibuilder.zip filemanager.zip robotcontrol.zip utilities.zip) do (
    tar -xf "%AUTOINSTALL_DIR%%%A" -C "%ADDONS_DIR%"
    del "%AUTOINSTALL_DIR%%%A"
)

:: --- PASO 9: ACTIVAR ADDONS EN BLENDER ---
set BLENDER_EXE=%AUTOINSTALL_DIR%blender-%BLENDER_VERSION%-windows-%TARGET_ARCH%\blender.exe
"%BLENDER_EXE%" -b --python-expr "import bpy; [bpy.ops.preferences.addon_enable(module=m) for m in ['archibuilder','filemanager','robotcontrol','utilities']]; bpy.ops.wm.save_userpref()"

