
# Robotcontrol editor toolbox - Blender addon.

*Robotcontrol editor toolbox* es un conjunto de herramientas creado para diseñar escenarios en 3D y controlar de forma remota plataformas robóticas. Es compatible para versiones superiores a 2.8 de *Blender*.

<center>
  <div class="column">
    <img src="images/ejecucion.gif" alt="Creacion de rutas">
    </div>
</center>

## Instalación.

En el último *release* se encuentra el código preparado para ser instalado.

### 1. Activar *addon Measureit*.

Para activar *Measureit* nos dirigimos a la pestaña preferencias : **Edit > Preferences**. Posteriormente, en la pestaña *add-ons*, buscamos *Measureit* y comprobamos que el *checklist* esté seleccionado.

<div class="row">
  <center>
  <div class="column">
    <img src="images/edit_preferences.png" alt="Edit menu" style="width:40%;float:left;padding: 5px;">
  </div>
  <div class="column">
    <img src="images/activate_addon.png" alt="Activate addon menu" style="width:60%;padding: 5px;">
  </div>
  </center>
</div>



### 2. Instalar *msgpack*.

**Msgpack** es un módulo de *Python* encargado de comprimir los paquetes utilizados en la comunicación con las plataformas robóticas.

Para instalarlo, seguimos los siguientes pasos:

1. Nos dirigimos a la carpeta donde tenemos instalado *Blender*.
2. Abrimos una terminal en **ruta-instalación-blender/blender-2.82a-windows64/blender-2.82a-windows64/2.82/python/bin/**.
3. Ejecutamos los siguientes comandos:
  1. **./python.exe -m pip install --upgrade pip**
  2. **./python.exe -m pip install msgpack**

### Instalar *addons*.

Al no estar distribuidos con la propia aplicación *Blender*, debemos instalarlos a partir de los 4 ficheros comprimidos en zip que se encuentran en zip del último *release* (*archibuilder.zip*, *robotcontrol.zip*, *utilities.zip* y *filemanager.zip*).

La instalación se realiza desde el panel de *Addons* de la ventana de preferencias.

Clicando en *Install...*, seleccionamos el fichero *zip* que deseamos instalar. Una vez instalado, nos debería aparecer automáticamente en el término de búsqueda. Si no es así, lo buscamos y lo activamos, al igual que lo hicimos con *Measureit*.

Estos pasos los repetimos con los 4 ficheros *zip* que disponemos.

Una vez completados estos pasos, guardamos las preferencias en la opción *Save preferences*.

## Funciones.

### Diseño de escenarios.

Con el addon *archibuilder*, se pueden crear paredes, habitaciones, techos y posicionar emisores de señales (*beacons*).
<br>
<br>

##### Crear paredes.

<div class="row">
  <div class="column">
    <img src="images/wall.png" alt="Pared" style="width:40%;float:left;padding: 5px;">
  </div>
  <div class="column">
    <img src="images/wall_menu.png" alt="Menu crear pared" style="width:50%;padding: 5px;">
  </div>
</div>
<br>
<br>

##### Crear habitaciones.

<div class="row">
  <div class="column">
    <img src="images/room.png" alt="habitación" style="width:40%;float:left;padding: 5px;">
  </div>
  <div class="column">
    <img src="images/room_menu.png" alt="Menu crear habitacion" style="width:50%;padding: 5px;">
  </div>
</div>
<br>
<br>

##### Crear techos.

<div class="row">
  <div class="column">
    <img src="images/ceil.png" alt="Techo" style="width:30%;float:left;padding: 5px;">
  </div>
  <div class="column">
    <img src="images/ceil_menu.png" alt="Menu crear techo" style="width:60%;padding: 5px;">
  </div>
</div>
<br>
<br>

##### Crear obstáculos.

<div class="row">
  <div class="column">
    <img src="images/obstacle.png" alt="Obstaculo" style="width:40%;float:left;padding: 5px;">
  </div>
  <div class="column">
    <img src="images/obstacle_menu.png" alt="Menu crear obstaculo" style="width:60%;padding: 5px;">
  </div>
</div>
<br>
<br>


##### Posicionar *beacons*.

<div class="row">
  <div class="column">
    <img src="images/bluetooth.png" alt="Beacon bluetooth" style="width:50%;float:left;padding: 5px;">
  </div>
  <div class="column">
    <img src="images/ultrasound.png" alt="Beacon" style="width:50%;padding: 5px;">
  </div>
</div>


<center>
<img src="images/beacon_menu.png" alt="Beacon bluetooth">
</center>
<br>
<br>

##### Exportar escenarios.

<center>
<img src="images/filemanager_interfaz.png" alt="Exportar escenarios">
</center>

### Control de plataformas robóticas.

Con el *addon robotcontrol* se pueden crear plataformas robóticas virtuales, con los que diseñar y ejecutar planes de navegación sobre un escenario.
<br>
<br>

#### Creación de plataformas robóticas.

<div class="row">
  <center>
  <div class="column">
    <img src="images/robot.png" alt="Beacon bluetooth" style="width:50%;float:left;padding: 5px;">
  </div>
  <div class="column">
    <img src="images/robot_menu.png" alt="Beacon" style="width:40%;padding: 5px;">
  </div>
  </center>
</div>

#### Diseño de planes de navegación.

<center>
  <div class="column">
    <img src="images/path_creation.gif" alt="Creacion de rutas">
    </div>
</center>


#### Ejecución de rutas.

Se pueden enviar rutas, pausar la plataforma, controlar su velocidad y cancelar planes de navegación.

<center>
  <div class="column">
    <img src="images/iniciar_plan.png" alt="Creacion de rutas">
    </div>
</center>

#### Simulación.

Sin necesidad de comunicarse con la plataforma se pueden simular planes de navegación creados, con controles similares al panel de control de la plataforma.


<center>
  <div class="column">
    <img src="images/panel_simulacion.png" alt="Creacion de rutas">
    </div>
</center>
