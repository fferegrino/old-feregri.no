---
layout: post
lannguage: es
title: Haciendo Web Scraping desde Gitlab
date: 2022-01-23 12:00:00
author: Antonio Feregrino
short_summary: Vamos a usar Gitlab para hacer web scraping diario de un sitio web del gobierno mexicano, ¿te animas?
lang: es
tags: python, gitlab, webscraping
sidebarimage: https://ik.imagekit.io/thatcsharpguy/posts/mananeras_74Gg9i3SC.jpg
---

El día de hoy quiero hablarles sobre un pequeño proyecto que comencé hace ya unos cuantos meses con la idea de analizar lo que el entonces [presidente de México](https://es.wikipedia.org/wiki/Andr%C3%A9s_Manuel_L%C3%B3pez_Obrador) en sus conferencias diarias. El objetivo de este proyecto era recolectar las transcripciones disponibles en el sitio web del gobierno, en esta sesión en vivo de YouTube les muestro [cómo hice parte de este proyecto](https://www.youtube.com/watch?v=8vL3FcK2QcQ).

> ⚠️ Esta es una solución rápida sin mucho pensamiento detrás ni muy buenas prácticas de desarrollo de software, y solamente lo presento como algo interesante que es un buen punto de inicio para tus proyectos.
> 

# 1. Python – Web Scraping

## Obteniendo las URLs

Cada una de las transcripciones existe en urls individuales, el primer paso es obtenerlas de la página de la Presidencia de México, la dirección URL es , toda la magia de este código sucede en el archivo [mananeras/dataset/download_urls.py](https://gitlab.com/thatcsharpguy/datasets/mananeras/-/blob/main/mananeras/dataset/download_urls.py). A resumidas cuentas, dentro de ese archivo tenemos una función llamada `get_new_urls`, que a resumidas cuentas:

1. Abre un archivo (llamado `urls.txt`) en donde previamente almacenamos las urls que ya descargamos (paso crucial si no queremos visitar una misma URL dos veces)
2. Consulta página por página el sitio del gobierno (`https://www.gob.mx/presidencia/es/archivo/articulos`) para encontrar nuevas URLs a transcripciones que no tengamos
3. Almacena las nuevas URLs que no hemos visitado en el archivo `urls.txt`
4. Regresa una lista con estas nuevas URLs

## Descargando las páginas web

El siguiente paso es recuperar las páginas en HTML de cada una de las nuevas URLs recuperadas en el paso anterior, esto sucede dentro de la función `download_articles` dentro del archivo [mananeras/dataset/download_articles.py](https://gitlab.com/thatcsharpguy/datasets/mananeras/-/blob/main/mananeras/dataset/download_articles.py), en la definición de esta función no hay mucha ciencia, lo único que hacemos es utilizar `urlretrieve` para descargar al disco local cada una de las páginas deseadas

## Extrayendo la información del HTML

Hasta este paso ya tenemos la información en forma “cruda”, el siguiente paso es utilizar un parser de HTML (como BeautifulSoup en Python) para pasar del formato HTML a otro que sea más amigable de trabajar. Esto se hace en la función `extract` dentro del archivo [mananeras/dataset/extract_dialogs.py](https://gitlab.com/thatcsharpguy/datasets/mananeras/-/blob/main/mananeras/dataset/extract_dialogs.py). Este archivo es tal vez la parte más compleja y frágil del código en Python y es que en donde leemos las etiquetas y conseguimos la información sobre los diálogos y hablantes en cada conferencia. Al terminar de ejecutarse, la función `extract` generará un archivo `txt` por cada `html` que tengamos.

## Publicando a Kaggle

Como yo cargo este [dataset a Kaggle](https://www.kaggle.com/ioexception/mananeras) es necesario comprimir la información en un archivo `zip`, esto se hace con una sola línea de código en Python: `shutil.make_archive("data/articulos", "zip", "./articulos")`.

Una vez comprimido uso la biblioteca que la misma gente de Kaggle publica para crear una nueva versión de mi dataset usando el método `dataset_create_version`.

```python
api.dataset_create_version("data", "Daily dataset update", dir_mode="zip", quiet=False)
```

Tras estas líneas se ha creado una nueva versión en Kaggle, el siguiente paso es automatizar todo este proceso, y aún mejor, agendarlo para que suceda una vez al día desde nuestro CI de Gitlab.

# 2. Configurando el web scraping desde Gitlab

Lo primero que vamos a definir es el popular archivo `.gitlab-ci.yml` en donde existe la configuración de nuestro *pipeline*, voy a mostrar sección y al final les mostraré todo el archivo:

## Imagen base

La primera cosa que especifico es la imagen base que el *runner* de CI debe usar, yo me decidí por una de Python 3.9

```yaml
image: python:3.9
```

## Dos etapas

Como buen desarrollador de software, también he incluido unas pruebas, es por eso que el pipeline consta de dos etapas: una para realizar algunas pruebas, y la otra, más importante, en donde ejecuto el código de Python descrito.

```yaml
stages:
  - test
  - create-datasset
```

## Preparación

Con la llave `before_script` lo que hacemos es especificar un conjunto de acciones que se deben llevar a cabo dentro de nuestra imagen `python:3.9` **antes** de que se ejecute cualquiera de nuestras instrucciones, a detalle, lo que hacemos es:

- Configurar *git* en el *runner*, específicamente quiero ponerle un correo y un nombre de usuario para que los commits que haga tengan esta información
- Instalar las dependencias necesarias para que mi código funciona, en mi caso, estoy usando [Poetry](https://python-poetry.org/).

```yaml
before_script:
  - git config --global user.email "runner@gitlab.com"
  - git config --global user.name "Antonio Feregrino"
  - pip install poetry
  - poetry config virtualenvs.create false --local
  - poetry install
```

## Ejecuta pruebas

El siguiente paso es ejecutar las pruebas usando *pytest*. Este paso es muy sencillo, simplemente ejecutamos `pytest tests/`.

```yaml
test:
  stage: test
  script:
    - pytest tests/
```

## Ejecuta el *web scraping*

Ahora sí, la parte más interesante, ejecutar el *web scraping*. Lo primero es que yo quiero ejecutar este paso **únicamente cuando una ejecución ha sido agendada**, es por eso que especifico una regla de ejecución en `rules`; Lo segundo es el conjunto de scripts que se deben ejecutar:

- Primero ejecutamos el módulo `mananeras` que justamente se encarga de coordinar todo el código de Python que expliqué anteriormente; este código modifica archivos dentro de la carpeta `articulos` y el archivo `url.txt`.
- Usamos `git add` para agregar estos dos archivos modificados al árbol de los cambios.
- Usamos `git commit` para confirmar los cambios a los archivos que acabamos de agregar.
- Usamos `git push` para cargar nuestros nuevos cambios al repositorio remoto de GitLab (sí, estamos haciendo un nuevo commit a Gitlab desde Gitlab)

De este modo nos aseguramos que los archivos que usamos para almacenar las urls que ya visitamos estén actualizados en este repositorio.

```yaml
crawl:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  stage: create-datasset
  script:
    - KAGGLE_KEY=$KAGGLE_KEY KAGGLE_USERNAME=ioexception python -m mananeras
    - git add articulos/ urls.txt
    - git diff --quiet && git diff --staged --quiet || git commit -m 'Nuevos archivos'
    - git push http://fferegrino:${CI_ACCESS_TOKEN}@gitlab.com/thatcsharpguy/datasets/mananeras.git HEAD:main
```

# 3. Configurando el pipeline

Hay algunas configuraciones que son necesarias para ejecutar el *pipeline* definido anteriormente, desde el menu de tu repositorio en Gitlab navega a **CI/CD > Schedules**. De ahí, da click en el botón que dice algo como **New schedule**. Esto te solicitará cierta información sobre cómo quieres que se llame, qué tan seguido quieres que se ejecute (mi pipeline de web scraping se ejecuta diario a las 19:20, usando el cron `20 19 * * *`) y en qué rama debe ser esta ejecución.

![https://ik.imagekit.io/thatcsharpguy/posts/menu_BK2nv98LO.png?ik-sdk-version=javascript-1.4.3&updatedAt=1642929857502](https://ik.imagekit.io/thatcsharpguy/posts/menu_BK2nv98LO.png?ik-sdk-version=javascript-1.4.3&updatedAt=1642929857502)

Y pues eso es todo, así es como [mi dataset en Kaggle se actualiza diariamente](https://www.kaggle.com/ioexception/mananeras) y un nuevo commit es creado en este repositorio, se que no es tan detallado (ni limpio) como podría haber sido, pero espero que te sirva para darte una idea de lo que se puede hacer con Gitlab y pon poco de imaginación.

Encuentra el [código para este post en Gitlab](https://gitlab.com/thatcsharpguy/datasets/mananeras/-/tree/post-version-1) para que tu también juegues con él, recuerda que me puedes encontrar en [Twitter @io_exception](https://twitter.com/io_exception) en donde estoy más que feliz de responder preguntas.
