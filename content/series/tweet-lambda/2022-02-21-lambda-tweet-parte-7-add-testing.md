---
layout: post
language: es
title: Agregando pruebas con Pytest – Bot con AWS Lambda: P7
date: 2022-02-21 10:00:07
short_summary: Vamos a usar GitHub actions para automatizar el provisionamiento de recursos con Terraform y la publicación de nuevas versiones de nuestra lambda.
tags: python, github, aws, terraform, github actions
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/cycles-part-6_DbKr-mcvk.jpg
slug: lambda-tweet-parte-7-add-testing
--- 

Esta serie de posts consta de 8 entregas, siendo esta la sexta en donde vamos a usar GitHub actions para automatizar el provisionamiento de recursos con Terraform y la publicación de nuevas versiones de nuestra lambda. Los otros posts en la serie abordan a su vez un aspecto muy específico del problema, puedes encontrarlos aquí:

 - Configurando Twitter y AWS - [Parte 1](/lambda-tweet-parte-1-github-aws-twitter)
 - Programando la lambda con Python - [Parte 2](/lambda-tweet-parte-2-python)
 - Mejorando el mapa con GeoPandas - [Parte 3](/lambda-tweet-parte-3-mapas-geopandas)
 - Creando la lambda en un contenedor - [Parte 4](/lambda-tweet-parte-4-contenedor-lambda)
 - Infraestructura con Terraform - [Parte 5](/lambda-tweet-parte-5-terraform)
 - Automatización con GitHub Actions - [Parte 6](/lambda-tweet-parte-6-github-actions)
 - Agregando pruebas con Pytest - [Parte 7](/lambda-tweet-parte-7-add-testing)
 - Optimizando Docker - [Parte 8](/lambda-tweet-parte-8-optimizando-docker)

---

Siguiendo en la serie de posts para crear una lambda que tuitee, en este post les voy a mostrar algo que en realidad debí hacer hace mucho tiempo... desde antes de poner la app en producción: vamos a probar nuestro código.

Para dotarle de organización a nuestro código, vamos a meter el código de la aplicación dentro de una carpeta llamada *src*, para mover ahí dentro los archivos necesarios de nuestra app:

```shell
mkdir src
git mv *.py src
```

Como ya habíamos copiado todos los archivos *.py* dentro de la imagen de la lambda, algo como esto:

```docker
COPY *.py ${LAMBDA_TASK_ROOT}/
```

Pero ahora vamos a tener que modificarla por esto

```docker
COPY src/*.py ${LAMBDA_TASK_ROOT}/
```

Otro cambio que hay que hacer es en nuestro archivo *terraform/main.tf*, este cambio es para que terraform siga siendo capaz de encontrar el código fuente de nuestra app dentro de la carpeta *src*:, dentro del recurso `"null_resource" "ecr_image"`:

```shell
		python_file_1 = filemd5("../src/app.py")
    python_file_2 = filemd5("../src/plot.py")
    python_file_3 = filemd5("../src/tweeter.py")
    python_file_4 = filemd5("../src/download.py")
```

Hasta este momento todo nuestro código debería seguir funcionando como antes.

## Testing con *pytest*

El primer paso es instalar la biblioteca *pytest*, como mencioné anteriormente, yo uso *pipenv*, tu puedes usar otro. A mi me gusta porque permite una división clara entre paquetes de desarrollo y dependencias necesarias para tu app, como *pytest* es de desarrollo, la instalo con la bandera `--dev`:

```shell
pipenv install --dev pytest
```

### Los tests

Yo recomiendo crear todas sus pruebas en una carpeta separada al código fuente, yo siempre uso una llamada *tests*.

```shell
mkdir tests
```

Mientras que es probable que tus tests sean más comprensivos, yo solo voy a comprobar que el método `execute` y en específico el método usado para generar el mapa a partir de un *data frame*. No me preocupa tanto la consulta a la API de TFL, ni que *Twython* haga bien su trabajo.

### Aislamiento

Tenemos que aislar nuestro método lo más posible, eso implica evitar que se consulte la API externa y evitar que algún Tweet sea generado. Para esto vamos a *“patchear”* los métodos que hacen estas tareas. 

Como necesitamos datos que reflejen la consulta a la API, extraje un subset de resultados y los guardé en un archivo llamado *sample.csv*:

```
name,lat,lon,bikes,empty_docks,docks,query_time,proportion
"Tanner Street, Bermondsey",51.500647,-0.0786,30,11,41,2022-02-18 18:40:00,0.7317073170731707
"Sancroft Street, Vauxhall",51.489479,-0.115156,18,5,24,2022-02-18 18:40:00,0.7916666666666666
"Bayley Street , Bloomsbury",51.518587,-0.132053,13,12,25,2022-02-18 18:40:00,0.52
"Tavistock Place, Bloomsbury",51.52625,-0.123509,9,9,19,2022-02-18 18:40:00,0.5263157894736842
"Harrington Square 1, Camden Town",51.533019,-0.139174,12,15,27,2022-02-18 18:40:00,0.4444444444444444
```

Vamos a leer este archivo y a regresar el resultado como un data frame cada que alguien llame al método `download_cycles_info`.

### Usando *fixtures*

Lo que vamos a hacer es crear una *fixture* de pytest, que en pocas palabras es un fragmento de código reutilizable. En pytest las fixtures toman forma de funciones decoradas con `@pytest.fixture`.

Dentro de esta fixture usamos la variable `pytestconfig` cuya propiedad `rootdir` nos dice cuál es el directorio desde el que ejecutamos nuestras pruebas; podemos usar esta variable para encontrar el archivo *csv* que acabamos de crear.

```python
from unittest.mock import patch
import pandas as pd
import pytest

@pytest.fixture
def patch_download_cycles_info(pytestconfig):
    sample_df = pd.read_csv(pytestconfig.rootdir / "tests" / "sample.csv")
    with patch("app.download_cycles_info", return_value=sample_df) as patched:
        yield patched
```

Una vez leído nuestro data frame, usamos `patch` para especificarle al código que cada llamada a `app.download_cycles_info` debe ser atajada y en su lugar regresar como retorno el dataframe que acabamos de leer. 

Por último, usamos `yield` en lugar de `return` para que nuestro `patch` se preserve hasta que la ejecución de la pureba termine.

### Método de prueba

Lo primero que recibe el método de prueba es la *fixture* `patch_download_cycles_info` que acabamos de definir anteriormente.

También recuerda que no quiero que el código tuitee durante pruebas, entonces hay que *“patchear”* el método `app.tweet` también.

```python
def test_exclude(patch_download_cycles_info):
    with patch("app.tweet") as tweet_patched:
        execute()
        patch_download_cycles_info.assert_called_once()
        tweet_patched.assert_called_once()
```

Después, ahora si podemos llamar al método `execute`. Solo para que una vez que se ejecutó comprobar que las llamadas a los métodos *“patcheados”* fuernon ejecutados con `assert_called_once`.

## Ejecutando las pruebas

Para facilitar la ejecución de pruebas, cree una instrucción en el *Makefile* que llama a *pytest* estableciendo que nuestro código fuente se encuentra en la carpeta *src* con la variable `PYTHONPATH`.

```makefile
test: shapefiles
	PYTHONPATH=src pytest tests/
```

Como quiero que estas pruebas se ejecuten en el *pipeline* de integración continua hay que modificar nuestro archivo de configuración de GitHub Actions, hay que gregar la bandera `--dev` a la hora de instalar los paquetes con *pipenv.* Y es necesaria también la bandera `--system` que instala las dependencias en el sistema *host*, no en un entorno virtual.

```yaml
- name: Install pipenv
  run: |
    pip install pipenv
    pipenv install **--dev**
```

Igualmente, hay que agregar un *step* que ejecute `make test` para correr las pruebas; yo puse la ejecución de pruebas antes de que la app genere el contenedor de la lambda.

```makefile
- name: Test local
  run: make test
```

¡Listo!, eso es todo con respecto a las pruebas.

Así es como se ve el repositorio al terminar este post: [fferegrino/tweeting-cycles-lambda at part-6-add-testing](https://github.com/fferegrino/tweeting-cycles-lambda/tree/part-6-add-testing).

Recuerda que me puedes encontrar en Twitter [en @io_exception](https://twitter.com/io_exception) para preguntarme sobre este post – si es que algo no queda tan claro o encontraste un *typo*. El código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon).