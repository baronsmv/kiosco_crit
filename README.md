# Kiosco de CRIT Hidalgo

Plataforma web que sirve información relevante a los pacientes y colaboradores
de CRIT Hidalgo a partir de consultas y envíos de formatos como PDF y Excel.

## Estructura

### Proyecto

El sistema está implementado como un proyecto Django (Python), el cual trabaja
a partir de apps (carpetas dentro del proyecto). La carpeta del proyecto se
encuentra en `kiosco_crit` y contiene:

- `settings.py`: El archivo de configuración global del proyecto.
- `urls.py`: Las rutas del proyecto, que incluye las rutas de cada app.

### Apps

Las apps del sistema en cuestión son:

- `menus`: Encargada de las vistas de menús (como principal, paciente y
  colaborador).
- `previews`: Encargada de la previsualización y descarga en PDF y en Excel.
- `queries`: Encargada de las consultas a la base de datos externa.
    - Asimismo, contiene la sub-app `apis`, encargada de los endpoints de cada
      consulta.
- `sendings`: Encargada del envío de archivos por e-mail y WhatsApp.

Aparte de esto, se incluyen directorios que son de apoyo al proyecto en general:

- `classes`: Diversas clases de Python usadas en las apps.
- `media` y `static`: Donde se sirve el contenido multimedia a la plataforma.
- `nginx`: Configuración del servidor Nginx.
- `scripts`: Scripts BASH, usados para diversas tareas secundarias.
- `utils`: Herramientas de apoyo general al proyecto.
- `whatsapp_node`: Modulo de WhatsApp, que actualmente requiere
  reimplementación debido a los cambios de WhatsApp.

#### Contenido de las apps

Cada app, especificado por Django, contiene archivos y carpetas relevantes
como:

- `admin.py`: Gestionar y registrar vistas web de administrador.
- `forms.py`: Crear formularios usados en plantillas.
- `migrations/`: Migraciones de modelos a la base de datos.
- `models.py`: Gestionar modelos de bases de datos.
- `static/`: Archivos estáticos como CSS y JS, usados por las plantillas.
- `templates/`: Plantillas web.
- `templatetags/`: Filtros de apoyo para plantillas web.
- `tests.py`: Implementar pruebas unitarias.
- `views.py`: Crear vistas web.

En el caso de aquellas que gestionan rutas, vistas y plantillas web, también
pueden contener:

- `contexts.py`: Configuración del contexto de variables que se pasan a las
  plantillas web.
- `selections.py`: Selección de columnas para cada vista (pantalla principal,
  datos del sujeto si hubiera, API, PDF y Excel).
- `utils.py`: Herramientas de apoyo a la app, como serialización.
- `urls.py`: Registro de rutas y conexión de éstas a las vistas web.

### Contenedores

El sistema se apoya en Docker Compose, herramienta de gestión de contenedores
Docker, el cual asegura escalabilidad de infraestructura y compatibilidad del
sistema en diversos entornos y servidores.

Los contenedores, configurados en `docker-compose.yml`, son:

- `django`: Contiene el proyecto Django.
- `redis`: Contiene el servidor Redis, usado para caché de consultas.
- `node` (deshabilitado actualmente): Contiene el modulo Node.js para las
  funciones de WhatsApp.
- `nginx`: Contiene el contenedor del servidor Nginx.
- `db`: Contiene la base de datos PostgresDB, que registra los eventos locales.
- `cleaner`: Contiene el sistema de apoyo para limpiar los archivos multimedia
  no recientes.
- `carousel`: Contiene el sistema de apoyo para guardar información

## Configuración

El archivo de entorno `.env.copy` sirve como ejemplo de la configuración
requerida para el proyecto. Se puede copiar a `.env`, especificando las
contraseñas de:

- `DB_PASSWORD`, la contraseña del usuario de la base de datos externa del
  CRIT.
- `POSTGRES_PASSWORD`, la contraseña a usar para la gestión de la base de datos
  interna.
- `EMAIL_HOST_PASSWORD`, la contraseña de la cuenta de correo electrónico a
  usar.

## Consultas

Cada consulta se divide en varias partes:

### 1. Campos SQL

En `queries/sql/select.py`, se encuentran los campos SQL reutilizables. Cada
uno se implementa usando la clase `SelectClause` (ubicada en
`classes/selections.py`), que contiene:

- `name`: El nombre que aparecerá en la página web y en los archivos
  multimedia.
- `sql_name`: El nombre usado en la consulta SQL como alias.
- `sql_expression`: La expresión SQL de ese dato en la base de datos.
- `format` (opcional): El formato a dar a ese dato. Por ejemplo, `name` se
  trata como un nombre, con las primeras letras de cada letra en mayúsculas.
- `required` (opcional, por defecto `False`): Es necesario para considerar
  completa a una columna de datos o, en caso contrario, duplicada por los
  `JOIN`.

De no existir el campo que se requiere, se puede agregar y usar.

### 2. Selección de campos SQL

Una vez estén los campos SQL con su respectiva instancia, se seleccionan para
cada consulta en `queries/sql/selections.py`. Cada consulta debe contener su
propia selección, implementada con la clase `SelectionList` (ubicada en
`classes/selections.py`), que puede incluir tuplas de campos para cada caso:

- `web`: Los campos a incluir en las vistas web.
- `subject`: Los campos a incluir para los datos de un sujeto (paciente,
  colaborador).
- `api`: Los campos a incluir para las APIs de esa consulta.
- `pdf`: Los campos a incluir para la creación de PDF.
- `excel`: Los campos a incluir para la creación de Excel.

Estas selecciones son opcionales, y la tupla `sql` agrupa todos los usados.

### 3. Query SQL

Es en `queries/sql/queries.py` que se implementan las queries como funciones.

Cada una incluye una query que usa la `SelectionList` del paso anterior, los
respectivos `JOIN` a las tablas correspondientes, y condiciones específicas.

### 4. Contexto web

En `queries/contexts.py` se definen los contextos web a usar en la vista de la
consulta. Los contextos web pasan variables a las plantillas para personalizar
su contenido.

Para los contextos, se usan diversas clases (ubicadas en `classes/contexts`),
pero la principal es `ContextList`, que contiene el contexto general necesario
para cada consulta.

`ContextList` se compone de los siguientes campos:

- `initial`: Una instancia de `InitialWebContext`, que contiene variables de la
  página web principal de cada consulta, donde se piden los datos y se incluye
  un botón de búsqueda. Los campos relevantes de esta instancia son:
    - `title`: El campo HTML `title`, que configura el nombre de la pestaña en
      el navegador.
    - `header`: El campo HTML de título, `h1`, que configura el título
      principal.
    - `id`: Una instancia de `IdSubContext`, que configura si se solicita el ID
      de un usuario en el formulario, así como otras especificaciones al
      respecto.
    - `date`: Una instancia de `DateSubContext`, que configura si se solicita
      una fecha en el formulario, así como otras especificaciones al respecto.
    - `home`: Una instancia de `HomeSubContext`, que configura si se muestra un
      enlace a un menú del sistema, así como otras especificaciones al
      respecto.
    - `search_button`: Una instancia de `SearchButtonSubContext`, que configura
      el botón de búsqueda.
- `modal`: Una instancia de `ModalContext`, que contiene variables del modal
  parcial de resultados. Éste configura títulos y subtítulos de los resultados,
  así como los botones de vistas previas y envíos por correo electrónico.
- `pdf`: Una instancia de `PDFContext`, que contiene variables usadas para
  generar el PDF de resultados. Contiene títulos, subtítulos y pie de página a
  mostrar.
- `redirect` (sin implementar actualmente en frontend): Una instancia de
  `RedirectContext`, que configura el redireccionamiento automático a algún menú
  después de determinado tiempo.
- `id_name` (opcional, usar si se pide un ID): El nombre del ID a solicitar
  (por ejemplo, `nombre de cuenta` o `número de carnet`).
- `subject_name` (opcional, usar si los datos resultantes son de una persona):
  El nombre de los usuarios a los que se hace referencia (por ejemplo,
  `paciente` o `colaborador`).
- `objects_name` (opcional, usar si se devuelven datos en forma de tabla): El
  nombre de los objetos a los que se hace referencia (por ejemplo, `citas`,
  `datos` o `espacios disponibles`).

### 5. Formulario de datos

En `queries/forms.py`, se reusa o crea el formulario a usar para recabar los
datos para la consulta. Actualmente hay tres:

- `BuscarIdForm`, que recibe un ID en forma de texto.
- `BuscarFechaForm`, que recibe una fecha.
- `BuscarIdFechaForm`, que recibe los dos anteriores.

El formulario por si solo no obliga al usuario a ingresar datos con el
parámetro de `required`, por lo que es necesario configurar eso en el contexto
inicial del paso anterior.

### 6. Vista web

En `queries/views.py`, se define la vista web de la consulta, que reusa la
función integradora `query_view` (ubicada en `queries/utils.py`), que recibe:

- `request`: El objeto `HttpRequest` recibido por la vista, que representa la
  solicitud HTTP del usuario.
- `query`: La función de consulta definida anteriormente.
- selection_list: La instancia de `SelectionList` que definimos anteriormente
  y configura las columnas de la consulta SQL.
- `context_list`: La instancia de `ContextList` que definimos anteriormente y
  configura los datos de la vista.
- `form`: La clase `Form` a usar para el manejo de datos en el formulario.
- `model` (opcional, por defecto el modelo `Consulta`): El modelo a usar para
  registrar en la base de datos local los eventos de consulta.
- `testing` (opcional, por defecto `False`): Una opción de prueba que devuelve
  datos de prueba en lugar de hacer consultas a la base de datos externa.

### 7. Ruta

En `queries/urls.py`, se define la URL que la vista web usará. Simplemente se
agrega a la lista `urlpatterns` usando la función `path` con la ruta relativa
a usar, la vista del paso anterior y el nombre (que se recomienda importar
desde el contexto que definimos).

El orden de las rutas es importante: las rutas más específicas deben ir
primero. Así, por ejemplo, si tenemos `citas/` y `citas/activas`, la segunda
debe preceder a la primera.

### 8. API Endpoint (opcional)

En `queries/apis/views.py` y `queries/apis/urls.py`, podemos definir las vistas
y rutas de la consulta que sirva como API endpoint para aplicaciones de
terceros o para scripts (como el de `carousel`, que obtiene los datos de
`citas disponibles` y los guarda en un JSON).

Para la vista, definimos los parámetros como parámetros de URL en la función,
y se usa la función integradora `api_query_view` (ubicada en
`queries/apis/utils.py`) de manera similar a `query_view` de la vista normal.
Lo único que cambia es que, en lugar de pasar el formulario, se pasa un
diccionario con los parámetros recibidos por la función.

Para la ruta, podemos definir varias rutas con diversos parámetros. El orden,
como en las rutas normales, importa.
