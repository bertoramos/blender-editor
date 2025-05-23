
# Robotcontrol editor toolbox - Blender addon.

*Robotcontrol editor toolbox* es un conjunto de herramientas creado para diseñar escenarios en 3D y controlar de forma remota plataformas robóticas. Es compatible para versiones superiores a 2.8 de *Blender*.

<p align="center">
  <img src="images/ejecucion.gif" alt="Creacion de rutas">
</p>
<p align="center">
Figura 1: Ejecución de plan de navegación.
</p>

## Instalación.

En el último *release* se encuentra el código preparado para ser instalado.

### 1. Descargar Blender.

Se recomienda descargar la versión portable de Blender. Para ello dirigirse a la url [https://www.blender.org/download/](https://www.blender.org/download/), seleccionar la versión de Blender requerida y elegir la versión portable.

Para crear una versión completamente portable, antes de la primera ejecución hay que crear una carpeta tal y como se explica en los siguientes recursos:

 * Versiones de Blender <4  : [https://docs.blender.org/manual/en/3.6/advanced/blender_directory_layout.html](https://docs.blender.org/manual/en/3.6/advanced/blender_directory_layout.html)
 * Versiones de Blender >=4 : [https://docs.blender.org/manual/en/4.4/advanced/blender_directory_layout.html#portable-installation](https://docs.blender.org/manual/en/4.4/advanced/blender_directory_layout.html#portable-installation)

### 2. Activar *addon Measureit*.

#### 2.1 Blender <4

Para activar *Measureit* nos dirigimos a la pestaña preferencias : **Edit > Preferences**. Posteriormente, en la pestaña *add-ons*, buscamos *Measureit* y comprobamos que el *checklist* esté seleccionado.

<p align="center">
<img src="images/edit_install.png" alt="Activate addon menu">
<!--![Activate addon menu](images/edit_install.png)-->
</p>
<p align="center">
Figura 2: Instalación de *addons*.
</p>

#### 2.2 Blender >=4

En las versiones >=4 la instalación cambia en algunos pasos. Para activar *Measureit* nos dirigimos a *Get extensions* y permitimos el acceso a internet *Allow Online Access*

<p align="center">
<img src="images/blender4-measureit-allowonline.png" alt="Activate addon menu">
<!--![Activate addon menu](images/edit_install.png)-->
</p>
<p align="center">
Figura 3: Permitir acceso a internet.
</p>

Posteriormente instalamos el *addon*.

<p align="center">
<img src="images/blender4-measureit-install.png" alt="Activate addon menu">
<!--![Activate addon menu](images/edit_install.png)-->
</p>
<p align="center">
Figura 4: Instalación de *addon*.
</p>

Si queremos comprobar que está activo, podemos dirigirnos a la pestaña *Addons* y buscamos *Measureit*, comprobando que el *checklist* esté activo.

### 3. Instalar dependencias Python.

#### 3.1. Instalar *msgpack*

**Msgpack** es un módulo de *Python* encargado de comprimir los paquetes utilizados en la comunicación con las plataformas robóticas.

Para instalarlo, seguimos los siguientes pasos:

1. Nos dirigimos a la carpeta donde tenemos instalado *Blender*.
2. Abrimos una terminal en **ruta-instalación-blender/blender-2.82a-windows64/blender-2.82a-windows64/2.82/python/bin/**.
3. Ejecutamos los siguientes comandos:
   1. **./python.exe -m ensurepip**
   2. **./python.exe -m pip install --upgrade pip**
   3. **./python.exe -m pip install msgpack**

> **_NOTA:_**  Las rutas y nombre de los ejecutables pueden variar ligeramente dependiendo de la versión de Blender y el sistema operativo. 

#### 3.2. Instalar *hid*

**HID** permite la entrada de periféricos.

Para instalar este módulo seguimos los mismos pasos explicados anteriormente, e instalamos con pip:

  1. **./python.exe -m pip install hid**

Además, debemos copiar en la ruta del ejecutable python (**ruta-instalación-blender/blender-2.82a-windows64/blender-2.82a-windows64/2.82/python/bin/**) la librería hidapi.dll. Se encuentra disponible en [https://github.com/libusb/hidapi/releases](https://github.com/libusb/hidapi/releases).

Posteriormente instalamos [x360ce](https://www.x360ce.com/). Mediante este programa podemos asignar las teclas de un mando genérico a uno de XBOX360. Seguimos las instrucciones de instalación en la web. 

IMPORTANTE: al ejecutar por primera vez el programa, ir a la pestaña ISSUES e instalar el driver en *Virtual Gamepad Emulation Driver*. 

Tras la instalación seguimos las instrucciones para asignar los controles de nuestro mando al de xbox.

### 4. Instalar *addons*.

Este *toolbox* debemos instalarlo a partir de los 4 ficheros comprimidos en zip que se encuentran dentro del archivo zip del último *release* (*archibuilder.zip*, *robotcontrol.zip*, *utilities.zip* y *filemanager.zip*).

La instalación se realiza desde el panel de *Addons* de la ventana de preferencias.

Clicando en *Install...*, seleccionamos el fichero *zip* que deseamos instalar. Una vez instalado, nos debería aparecer automáticamente en el término de búsqueda. Si no es así, lo buscamos y lo activamos, al igual que lo hicimos con *Measureit*.

Estos pasos los repetimos con los 4 ficheros *zip* que disponemos.

Una vez completados estos pasos, guardamos las preferencias en la opción *Save preferences*.

## Funciones.

> **_NOTA:_**  La interfaz de todas las funciones del addon están localizadas en las distintas pestañas del panel lateral [(también conocido en la comunidad como N-panel)](https://docs.blender.org/manual/en/latest/editors/3dview/introduction.html#sidebar-region). Pulsa la tecla N para abrirlo o cerrarlo.


### Diseño de escenarios.

Con el addon *archibuilder*, se pueden crear paredes, habitaciones, techos y posicionar emisores de señales (*beacons*).
<br>
<br>

#### Crear paredes.

Se pueden crear paredes con las que delimitar un escenario virtual.

<p align="center">
<img src="images/wall_create.png" alt="Crear paredes">
<!--![Crear paredes](images/wall_create.png)-->
</p>
<p align="center">
Figura 5: Creación de paredes.
</p>

#### Crear habitaciones.

Utilizando paredes, se facilita la creación de habitaciones, que pueden modificarse.

<p align="center">
<img src="images/room_create.png" alt="Crear habitaciones">
<!--![Crear habitaciones](images/room_create.png)-->
</p>
<p align="center">
Figura 6: Creación de habitaciones.
</p>

#### Crear techos.

Los techos se representan como planos semitransparentes. Pueden situarse sobre el escenario, para delimitar su altura.

<p align="center">
<img alt="Crear techos" src="images/ceil_create.png">
<!--![Crear techos](images/ceil_create.png)-->
</p>
<p align="center">
Figura 7: Creación de techos.
</p>

#### Crear obstáculos.

Los obstáculos representan zonas en las que las plataformas robóticas no pueden adentrarse.

<p align="center">
<img alt="Crear obstáculos" src="images/obstacle_create.png">
<!--![Crear obstáculos](images/obstacle_create.png)-->
</p>
<p align="center">
Figura 8: Creación de obstáculos.
</p>

#### Posicionar *beacons*.

Los *beacons* son emisores de señales que utiliza la plataforma robótica para orientarse en el escenario real. En el escenario virtual son utilizados como información adicional al usuario, para conocer donde están situados en la realidad.

<p align="center">
<img src="images/beacon_create.png" alt="Crear beacon">
<!--![Crear beacons](images/beacon_create.png)-->
</p>
<p align="center">
Figura 9: *Beacon bluetooth* y ultrasónico.
</p>

<p align="center">
<img src="images/beacon_menu.png" alt="Beacon menu">
</p>
<p align="center">
Figura 10: Menú de creación de beacons.
</p>
<br>
<br>

#### Exportar escenarios.

Los escenarios diseñados pueden exportarse a ficheros ***.blend***.

<p align="center">
<img src="images/filemanager_interfaz.png" alt="Exportar escenarios">
</p>
<p align="center">
Figura 11: Menú exportar escenarios.
</p>

### Control de plataformas robóticas.

Con el *addon robotcontrol* se pueden crear plataformas robóticas virtuales, con los que diseñar y ejecutar planes de navegación sobre un escenario.
<br>
<br>

#### Creación de plataformas robóticas.

El *addon* está adaptado para poder diseñar múltiples tipos de plataformas robóticas. Por el momento, solamente se encuentra implementado el diseño de *RoboMap*.

<p align="center">
<img src="images/robot_create.png" alt="Crear robots">
<!-- ![Crear robots](images/robot_create.png)-->
</p>
<p align="center">
Figura 12: Creación de plataformas robóticas.
</p>

#### Diseño de planes de navegación.

Siempre que exista una plataforma robótica en el escenario virtual, pueden crearse planes de navegación, que pueden ser enviados a la plataforma real para que los ejecute, o simularlos en la propia aplicación.

<p align="center">
  <img src="images/path_creation.gif" alt="Creacion de rutas">
</p>
<p align="center">
Figura 13: Creación de ruta.
</p>

#### Ejecución de rutas.

Se pueden enviar rutas, pausar la plataforma, controlar su velocidad y cancelar planes de navegación.

<p align="center">
  <img src="images/iniciar_plan.png" alt="Menu control de plataforma">
</p>
<p align="center">
Figura 14: Panel de control de plataformas.
</p>

#### Simulación.

Sin necesidad de comunicarse con la plataforma se pueden simular planes de navegación creados, con controles similares al panel de control de la plataforma.

<p align="center">
  <img src="images/panel_simulacion.png" alt="Creacion de rutas">
</p>
<p align="center">
Figura 15: Menú de control de la simulación.
</p>

#### Telecontrol

Para activar el telecontrol, pulsar el botón *Open manual control* en la interfaz. Seleccionamos en el cuadro de diálogo nuestro dispositivo.

- Para utilizar el teclado seleccionamos  en el desplegable *keyboard*.
- Para utilizar *x360ce*, abrimos el ejecutable *x360ce.exe*, asignamos controles y minimizamos para dejar en segundo plano. Posteriormente seleccionamos en el desplegable el dispositivo *"Controller (XBOX 360 For Windows)"*.

##### Control con *gamepad*.

- Joystick izquierdo: Dirección de movimiento.
- L: rotar a la izquierda
- R: rotar a la derecha
- X/Y/A/B: parar

##### Control con teclado.

- V: Activar/desactivar el movimiento. La plataforma se mueve continuamente en la dirección actual.
- K/L : Ajustar dirección de la plataforma 1 grado a la izquierda/derecha.
- W/S/A/D : Cambiar dirección hacia adelante/atrás/izquierda/derecha.
- Flecha izquierda/derecha: rotar en sentido antihorario/horario.

## Referencias

Acceso a publicación en el repositorio Acceda: [http://hdl.handle.net/10553/77830](http://hdl.handle.net/10553/77830)
