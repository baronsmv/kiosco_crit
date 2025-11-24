# Kiosco de CRIT Hidalgo

Plataforma web que sirve información relevante a los pacientes y colaboradores
de CRIT Hidalgo a partir de consultas y envíos de formatos como PDF y Excel.

## Especificaciones técnicas

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
- `node` (deshabilitado actualmente): Contiene el modulo Node.js para las
  funciones de WhatsApp.
- `nginx`: Contiene el contenedor del servidor Nginx.
- `db`: Contiene la base de datos PostgresDB, que registra los eventos locales.
- `cleaner`: Contiene el sistema de apoyo para limpiar los archivos multimedia
  no recientes.
- `carousel`: Contiene el sistema de apoyo para guardar información

## Consultas

Cada consulta se divide en varias partes:

### Campos SQL

En `queries/sql/select.py`, se encuentran los campos SQL reutilizables. Cada
uno se implementa usando la clase `SelectClause`, que contiene:

- `name`: El nombre que aparecerá en la página web y en los archivos
  multimedia.
- `sql_name`: El nombre usado en la consulta SQL como alias.
- `sql_expression`: La expresión SQL de ese dato en la base de datos.
- `format` (opcional): El formato a dar a ese dato. Por ejemplo, `name` se
  trata como un nombre, con las primeras letras de cada letra en mayúsculas.

De no existir el campo que se requiere, se puede agregar y usar.

### Selección de campos SQL

Una vez estén los campos SQL con su respectiva instancia, se seleccionan para
cada consulta en `queries/sql/selections.py`. Cada consulta debe contener su
propia selección, implementada con la clase `SelectionList`, que puede incluir
tuplas de campos para cada caso:

- `web`: Los campos a incluir en las vistas web.
- `subject`: Los campos a incluir para los datos de un sujeto (paciente,
  colaborador).
- `api`: Los campos a incluir para las APIs de esa consulta.
- `pdf`: Los campos a incluir para la creación de PDF.
- `excel`: Los campos a incluir para la creación de Excel.

Estas selecciones son opcionales, y la tupla `sql` agrupa todos los usados.

### Query SQL

Es en `queries/sql/queries.py` que se implementan las queries como funciones.

Cada una incluye un query que usa la `SelectionList` del paso anterior, los
respectivos `JOIN` a las tablas correspondientes, y condiciones. Finalmente,
se incluye en la función `parse_query` con los parámetros de la consulta, que
se encarga de incluir condiciones y filtros dependientes de la fecha.

### Context web

### Vista web
