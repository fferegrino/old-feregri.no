---
layout: post
language: es
title: Dockerizando el código – Bot con AWS Lambda: P4
date: 2022-02-02 10:00:04
short_summary: Vamos a empaquetar nuestro código en Python dentro de un contenedor para que AWS lo use al ejecutar la lambda.
tags: python, github, aws
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/cycles-part-4_ck6phbCDbl.jpg
slug: lambda-tweet-parte-4-contenedor-lambda
--- 

Esta serie de posts consta de 6 entregas, siendo esta la cuarta en donde vamos a empaquetar nuestro código en Python dentro de un contenedor para que AWS lo use al ejecutar la lambda. Los otros posts en la serie abordan a su vez un aspecto muy específico del problema, puedes encontrarlos aquí:

 - Configurando Twitter y AWS - [Parte 1](/lambda-tweet-parte-1-github-aws-twitter)
 - Programando la lambda con Python - [Parte 2](/lambda-tweet-parte-2-python)
 - Mejorando el mapa con GeoPandas - [Parte 3](/lambda-tweet-parte-3-mapas-geopandas)
 - Creando la lambda en un contenedor - [Parte 4](/lambda-tweet-parte-4-contenedor-lambda)
 - Infraestructura con Terraform - [Parte 5](/lambda-tweet-parte-5-terraform)
 - Automatización con GitHub Actions - [Parte 6](/lambda-tweet-parte-6-github-actions)

---

La idea de las *lambdas* en AWS es que es código que no está constantemente en ejecución en un servidor (de ahí que se le conozca como *serverless* al paradigma); las *lambdas* se ejecutan bajo demanda y durante un corto tiempo.

Crear una *lambda* es trivial cuando nuestro código no tiene dependencias a paquetes de terceros; pero ya sabemos que ese no es nuestro caso – tenemos dependencias con diversos paquetes: *pandas*, *matplotlib*, *seaborn*, *geopandas* y *twython*, además de unos cuantos archivos que contienen el mapa.

Te podrás preguntar: si “no hay servidor”, ¿en dónde instalo estas dependencias? y la respuesta que nos da AWS esta formada de 3 soluciones, las voy a listar y te contaré por qué no elegí esa ruta:

- Puedes [incluir tus dependencias dentro de un archivo *.zip*](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) junto con tu código – las dependencias y archivos necesarios exceden el tamaño máximo soportado.
- Puedes crear algo conocido como capas, que pueden contener dependencias y otros archivos necesarios para la ejecución de las funciones – no opté por esta por el tamaño de las dependencias (que es igual a la del *.zip* del punto anterior), en realidad las capas son una buena opción para compartir dependencias entre varias *lambdas*.
- Puedes crear un contenedor y ejecutar tu lambda usándolo – es la opción por la que opté, además de hacer el despliegue más sencillo porque la limitación del tamaño ya no es problema para mi, y me permite probar la lambda localmente (ya saben que a mi me fascina poder ejecutar cosas localmente)

# Dependencias

Mi idea es hacer el contenedor lo más ligero posible, así que antes de empaquetar las dependencias de Python necesito exportar las dependencias de *pipenv* al popular *requirement.txt*, no quiero instalar *pipenv* en el contenedor (como dije al inicio de estos posts, no es necesario que uses *pipenv* para gestionar tus dependencias).

Cree una instrucción en el *Makefile* para generar el archivo *requirements.txt*:

```makefile
requirements.txt:
	pipenv lock -r > requirements.txt
```

También hay que descargar los archivos *shapefile* – igual recuerda que me hice una instrucción en el *Makefile* para descargarlos:

```makefile
shapefiles:
	wget https://data.london.gov.uk/download/statistical-gis-boundary-files-london/9ba8c833-6370-4b11-abdc-314aa020d5e0/statistical-gis-boundaries-london.zip
	unzip statistical-gis-boundaries-london.zip
	mkdir -p shapefiles
	mv statistical-gis-boundaries-london/ESRI/London_Borough_Excluding_MHW* shapefiles/
	rm -rf statistical-gis-boundaries-london statistical-gis-boundaries-london.zip
```

# Entrada a nuestra *app*

Previamente creamos un archivo llamado *app.py* que contiene un método que agrega las funciones que creamos previamente. Es en este archivo que agregaremos el punto de entrada de nuestra *lambda* – puede tener cualquier nombre pero siempre debe recibir dos argumentos; para el nombre convencionalmente se le llama `handler`:

```python
def handler(event, context):
    execute()
    return {"success": True}
```

El valor de retorno debe ser un objeto que sea serializable, en mi caso, regreso un diccionario.

# Dockerfile

Para crear el contenedor de la *lambda* usaré Docker, y como ya lo he dicho en múltiples ocasiones, las *Dockerfiles* son las recetas que usamos para crear contenedores. Este es el archivo que usaré:

```docker
FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt .

COPY shapefiles/ ./shapefiles/

RUN pip3 install -r requirements.txt

COPY *.py ./

CMD ["app.handler"]
```

Vamos paso por paso:

1. `FROM ...`:  a pesar de que podemos usar casi cualquier imagen como base, AWS nos ofrece unas con funcionamiento garantizado, `public.ecr.aws/lambda/python:3.8` es un ejemplo de ellas.
2. `COPY requirements.txt ...`: Copiamos el archivo con nuestras dependencias
3. `COPY shapefiles/ ...`: Copiamos nuestra carpeta de *shapefiles*
4. `RUN pip3 insta...`: instala las dependencias descritas en el archivo correspondiente
5. `COPY *.py ...`: Copia los archivos de la aplicación al contenedor
6. `CMD ["app...`: le especifica al contenedor cuál es el punto de entrada a nuestra *lambda*

Para construir la imagen basta ejecutar un comando como el siguiente:

```bash
docker build -t lambda-cycles .
```

De igual manera, cree una instrucción en el *Makefile* para crear la imagen:

```makefile
container: shapefiles requirements.txt
	docker build -t lambda-cycles .
```

# Probando localmente

La gran ventaja de usar contenedores es que podemos ejecutar la lambda localmente, por ejemplo, una vez que crees una imagen con el *Dockerfile* anterior, puedes ejecutarlo de la siguiente manera.

Es importante que utilices las banderas `-p` y `-e`, la primera para especificar un *mappeo* de puertos entre el *8080* del contenedor y el *9000* del host. La segunda es para especificar variables de entorno para el contenedor, estos deben ser los secretos de Twitter que habíamos obtenido previamente.

```bash
docker run \
    -p 9000:8080 
    -e API_KEY="ACTUAL VALUE FOR API_KEY" \
    -e API_SECRET="ACTUAL VALUE FOR API_SECRET" \
    -e ACCESS_TOKEN="ACTUAL VALUE FOR ACCESS_TOKEN" \
    -e ACCESS_TOKEN_SECRET="ACTUAL VALUE FOR ACCESS_TOKEN_SECRET" \
        hello-world
```

Luego, desde otra terminal, puedes ejecutar la *lambda* con *curl:*

```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
		-d '{}'
```

Así es como [se ve el repositorio](https://github.com/fferegrino/tweeting-cycles-lambda/tree/part-3-dockerise) al terminar este post.

Recuerda que me puedes encontrar en Twitter [en @io_exception](https://twitter.com/io_exception) para preguntarme sobre este post – si es que algo no queda tan claro o encontraste un *typo*. El código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon) 
