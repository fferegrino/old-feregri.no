---
layout: post
language: es
title: Optimizando Docker – Bot con AWS Lambda: P8
date: 2022-02-21 10:00:08
short_summary: Voy a reducir el tamaño de la imagen hecha con Docker, una reducción de más de 50% para reducir costos y hacer más eficiente nuestro pipeline.
tags: python, github, aws, docker
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/8-optimising-docker.jpg
slug: lambda-tweet-parte-8-aligerando-docker
--- 

Esta serie de posts consta de 8 entregas, siendo esta la octaba en donde voy a reducir el tamaño de la imagen hecha con Docker, una reducción de más de 50% para reducir costos y hacer más eficiente nuestro pipeline. Los otros posts en la serie abordan a su vez un aspecto muy específico del problema, puedes encontrarlos aquí:

 - Configurando Twitter y AWS - [Parte 1](/lambda-tweet-parte-1-github-aws-twitter)
 - Programando la lambda con Python - [Parte 2](/lambda-tweet-parte-2-python)
 - Mejorando el mapa con GeoPandas - [Parte 3](/lambda-tweet-parte-3-mapas-geopandas)
 - Creando la lambda en un contenedor - [Parte 4](/lambda-tweet-parte-4-contenedor-lambda)
 - Infraestructura con Terraform - [Parte 5](/lambda-tweet-parte-5-terraform)
 - Automatización con GitHub Actions - [Parte 6](/lambda-tweet-parte-6-github-actions)
 - Agregando pruebas con Pytest - [Parte 7](/lambda-tweet-parte-7-add-testing)
 - Optimizando Docker - [Parte 8](/lambda-tweet-parte-8-aligerando-docker)

---

Recibí un correo electrónico de AWS, diciéndome que estaba excediendo mi presupuesto de usuo gratuito usando mucho almacenamiento en el servicio de ECR, en donde se almacena la imagen de mi *lambda*.

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/aws-alert.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/aws-alert.png)

Fui a revisar y pues sí, la imagen comprimida en AWS consume *~422.08MB*, que es un tamaño grande, aún para todas las dependencias que contamos.

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/image-size.png?ik-sdk-version=javascript-1.4.3&updatedAt=1645372286895](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/image-size.png?ik-sdk-version=javascript-1.4.3&updatedAt=1645372286895)

También revisé el tamaño de la imagen descomprimida usando `docker image ls lambda-cycles` y el resultado es un gigantesco *1.14GB*:

```
REPOSITORY      TAG       IMAGE ID       CREATED             SIZE
lambda-cycles   latest    987a563a70e5   About an hour ago   1.14GB
```

He de aceptarlo, no hice un esfuerzo magnifico por hacer ligera la primera imagen que cree [en el 4to post](https://feregri.no/lambda-tweet-parte-4-contenedor-lambda/) de esta serie. En este post voy a corregir eso.

## Adiós a la imagen provista por AWS

La imagen provista por AWS que usé en el pasado es un buen punto de inicio, sin embargo no es lo ideal si queremos aligerar el tamaño de la imagen. Para comenzar usaré una imagen oficial de Python, la clave está en la versión a usar.

Elegí `3.8-slim-buster` después de experimentar con otras, de entrada quiero usar Python 3.8, y estoy buscando una imagen ligera que requiera de mínima configuración para instalar las dependencias de la lambda, de ahí la elección de *slim-buster*.

## *Multi-stage* Dockerfile

Para lograr un tamaño lo más pequeño posible, haré uso de la funcionalidad *multi-stage build* provista por *Docker*, que permite la creación de múltiples imagenes en un solo *Dockerfile*.

Una de las ideas detrás de las mutli-stage build es que podemos usar una imagen para compilar el código fuente de nuestra app y de ahí copiarla a una imagen final, más optimizada para ponerla en producción. Verás cómo es que la uso a continuación.

Antes de comenzar, hay que definir unos argumentos antes de continuar. El primero es el directorio en donde voy a instalar las dependencias de nuestra lambda, el segundo argumento es la etiqueta de la imagen que usaremos.

```docker
ARG FUNCTION_DIR="/var/task"
ARG PYTHON_IMAGE=3.8-slim-buster
```

## `build-image`

La primera imagen a construir es una en donde voy a instalar todas las dependencias de la lambda.

```docker
# Base image
FROM python:${PYTHON_IMAGE} AS build-image

ARG FUNCTION_DIR

RUN mkdir -p ${FUNCTION_DIR}
```

- Con `FROM` ... especifico que imagen voy a usar, con `AS` le especifico un nombre a esta imagen
- Con `ARG FUNCTION_DIR` capturo el valor del argumento definido anteriormente – de otro modo no está disponible al momento de construir `build-image`.
- Y luego podemos hacer uso de este argumento para crear el directorio para el código.

Sigue la parte  “pesada” de la construcción de la imagen; la instalación de unos cuantas bibliotecas del sistema operativo necesarias para instalar las dependencias de Python, en mi caso particular *GeoPandas* necesita algunas cuantas bibliotecas de calculos geoespaciales (*gdal*). Tu caso puede variar.

```docker
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      binutils \
      g++ \
      gdal-bin \
      libgdal-dev \
      libproj-dev \
      python-gdal \
      python3-gdal
```

Por último, copio e instalo las dependencias de la *lambda*, adicionalmente también hay que instalar el *Lambda Runtime Interface Client* (`awslambdaric`) – necesario para ejecutar el código de la *lambda*.

```docker
COPY requirements.txt ./

RUN pip install --compile --target ${FUNCTION_DIR} awslambdaric && \
    pip install --compile --target ${FUNCTION_DIR} -r requirements.txt
```

Hasta aquí termina la parte de esta imagen.

## `test-app`

Quiero construir una imagen para probar el código de la lambda en un entorno parecido a producción. 

Como puedes ver, se puede usar una imagen previa como base. Abajo estoy usando `build-image` para crear otra llamada `test-app`.

```docker
FROM build-image AS test-app
```

El siguiente paso es copiar el archivo con las dependencias de desarrollo:

```docker
COPY requirements-dev.txt ./
RUN pip install --target ${FUNCTION_DIR} -r requirements-dev.txt
```

Por último copio todos los archivos incluyendo los archivos de código fuente de la app incluyendo los archivos de prueba

```docker
WORKDIR ${FUNCTION_DIR} 
COPY ./src/*.py ${FUNCTION_DIR}/
COPY ./shapefiles ${FUNCTION_DIR}/shapefiles
COPY ./tests ${FUNCTION_DIR}/tests
```

Si te das cuenta, el tema de toda esta imagen es el de ejecutar pruebas, acá no es tan importante el tamaño de la imagen, es por eso que no nos preocupa optimizar al máximo, es por eso que sigo usando la imagen base anterior.

## `app`

Por último, falta la parte más importante de la *lambda*: el contenedor principal. Este es el del tamaño más optimizado.

Es por eso que con esta comienzo con una copia fresca de `python:3.8-slim-buster`, como en los casos, capturo el argumento `FUNCTION_DIR` para usarlo en la imagen.

```docker
FROM python:${PYTHON_IMAGE} AS app
ARG FUNCTION_DIR
```

Acá esta la magia de las *multi-stage* builds, porque gracias a se puede copiar archivos entre imágenes, se sigue usando la instrucción `COPY` en conjunto con la bandera `—from` para especificar la imagen origen. Si recuerdas, fue en `build-image` en donde instalé la las dependencias, gracias a que ya descargué los paquetes en la imagen `build-image` solamente tengo que copiarlas. Así me ahorro instalar los paquetes del sistema operativo.

```docker
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
```

En este caso copio los archivos de mi app, aquí hay que notar que no copio los archivos de la carpeta *tests*.

```docker
COPY ./src/*.py ${FUNCTION_DIR}/
COPY ./shapefiles ${FUNCTION_DIR}/shapefiles
```

Por último establezco la carpeta de inicio con `WORKDIR`, para después establecer el punto de entrada del contenedor y el comando a ejecutar cuando este se inicie. En el caso de las lambdas, hay que establecer el punto de entrada al modulo `awslambdaric`.

```docker
WORKDIR ${FUNCTION_DIR}
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.handler" ]
```

## Building the test image

Ahora, para poder construir la imagen de prueba necesitamos un archivo de requerimientos de desarrollo – el siguiente comando de *pipenv* permite crear un archivo con las dependencias:

```makefile
requirements-dev.txt:
	pipenv lock --dev -r > requirements-dev.txt
```

Una vez que ya está el archivo de requerimientos ya se puede construir la imagen de prueba con el siguiente comando, nota que le puse un prefijo al nombre de la imagen, y que estoy usando la bandera `—target test-app`, con `—target` se le indica a docker qué imagen construir.

```makefile
test-container: shapefiles requirements-dev.txt
	docker build -t test-lambda-cycles --target test-app .
```

Puse todas estas instrucciones en un Makefile para hacer todo más sencillo.

## Probando dentro del contenedor

De nada sirve crear una imagen de prueba si no la uso, para ejecutar las pruebas dentro del contenedor es posible usar docker run, lo que tengo que hacer es sobreescribir el punto de entrada con `—entrypoint`, y especificar cuál es el comando a ejecutar, en mi caso `python -m pytest tests/` que ejecutará las pruebas.

```makefile
run-test-container:
	docker run -t --entrypoint '' test-lambda-cycles python -m pytest tests/
```

Igualmente agregué un nuevo paso al *pipeline* de CI, para ejecutar estas pruebas de forma automática, usualmente las pruebas que requieren de contenedor se deben ejecutar después de construir el contenedor pero antes de que se publique en algún repositorio, para prevenir que en el repositorio haya código que no funciona.

```yaml
		- name: Build and run test image
      run: |
        make test-container
        make run-test-container
```

## Construyendo la nueva imagen final

Tengo que cambiar la forma en que se construye la imagen final de la *lambda*; hay que especificar cuál es la imagen a construir usando `--target`, en este caso `app`. 

```makefile

container:
	docker build -t lambda-cycles --target app .
```

Para corroborar que logré reducir el tamaño de la imagen, voy a ejecutar `docker image ls lambda-cycles`:

```
REPOSITORY      TAG       IMAGE ID       CREATED          SIZE
lambda-cycles   latest    74a3b0058c86   14 seconds ago   529MB
```

Así es, **pasamos de una imagen de ~*1.14GB* a una de *529MB***, una reducción de ~50%; vale la pena, ¿no?

## Ejecutando la imagen localmente

Si quieres ejecutar localmente la lambda, tal vez para asegurarte de que funciona manualmente, es necesario que descargues un emulador de AWS, el la siguiente instrucción dentro del *Makefile* hace precisamente eso.

```makefile
.aws-lambda-rie:
	mkdir -p ./.aws-lambda-rie && curl -Lo ./.aws-lambda-rie/aws-lambda-rie \
		https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && \
		chmod +x ./.aws-lambda-rie/aws-lambda-rie
```

Este *snippet* de código lo encontré en la documentación misma de AWS: [testing Lambda container images locally](https://docs.aws.amazon.com/lambda/latest/dg/images-test.html#images-test-add).

Una vez que ya está el emulador de la lambda descargado ahora si ya la puedo ejecutar localmente, el siguiente comando de docker es complejo por todas las opciones que hay que establecer, así que trataré de explicarlo:

```shell
docker run \
	-v ~/.aws-lambda-rie:/aws-lambda \
	-p 9000:8080 \
	-e LAMBDA_TASK_ROOT="/var/task" \
	-e LAMBDA_RUNTIME_DIR="/var/runtime" \
	-e API_KEY="${API_KEY}" \
	-e API_SECRET="${API_SECRET}" \
	-e ACCESS_TOKEN="${ACCESS_TOKEN}" \
	-e ACCESS_TOKEN_SECRET="${ACCESS_TOKEN_SECRET}" \
  --entrypoint /aws-lambda/aws-lambda-rie lambda-cycles \
  		/usr/local/bin/python -m awslambdaric app.handler
```

Estoy ejecutando la imagen `lambda-cycles` con `docker run`, al cual le paso las siguientes opciones:

- `-v`: para montar el directorio (*~/.aws-lambda-rie*) donde descargamos el emulador en el directorio */aws-lambda* dentro del contenedor en ejecución.
- `-p`: para especificar un mapeo de puertos, del *8080* en el contenendor al *9000* en la máquina host.
- `-e`: para especificar un montón de variables de entorno, las dos primeras: `LAMBDA_TASK_ROOT` y `LAMBDA_RUNTIME_DIR` son variables que define AWS en tiempo de ejecución y las otras ya las conoces, son las que se necesitan para tuitear.
- `--entrypoint`: para sobreescribir el punto de entrada de la lambda, en este caso se establece al emulador que descargamos previamente y que pusimos disponible dentro del contenedor con `-v`.

Una vez que el contenedor con la *lambda*, se está ejecutando, es posible llamarla con *curl* usando otra terminal:

```shell
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
        -d '{}'
```

Así es como se ve el repositorio al terminar este post: [fferegrino/tweeting-cycles-lambda at part-7-optimise-docker](https://github.com/fferegrino/tweeting-cycles-lambda/tree/part-7-optimise-docker).

Recuerda que me puedes encontrar en Twitter [en @io_exception](https://twitter.com/io_exception) para preguntarme sobre este post – si es que algo no queda tan claro o encontraste un *typo*. El código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon).