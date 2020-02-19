---
layout: post
language: es
original_url: https://dev.to/fferegrino/creando-una-lambda-en-aws-usando-pipenv-14mh
title: Creando una AWS lambda con python
date: 2020-01-28 10:00:00
tags: aws, aws-lambda, python, pip
short_summary: I will try to guide you when you are about to create a function that operates under the serverless paradigm.
---
Las lambdas de AWS representan una de las soluciones más comunes cuando desarrollando aplicaciones *serverless*. En este post, trataré de cubrir cómo desarrollar, comprimir, desplegar y configurar una función, la cual correrá en la computadora de alguien más.

Si no sabes qué es el "serverless", te invito a ver mi video [AWS Lambdas y el paradigma serverless](https://youtu.be/lWgP41J6Wyo) en el que explico más sobre el tema.

<small><strong>This post is also available in english, [click here](https://dev.to/fferegrino/creating-an-aws-lambda-using-pipenv-2h4a) to read it.</strong></small>

### Desarrollo

Como vamos a estar utilizando python, es muy recomendable que creemos un entorno virtual y lo activemos antes de comenzar.

```shell
python -m venv env
source env/bin/activate
```

Solo entonces podemos instalar las librerías que vamos a usar en nuestra lambda, en nuestro caso solamente usaremos `requests` y `twython`:

```shell
pip install requests twython 
```

Una vez hecho esto, podemos continuar desarrollando nuestra función. Y es tan simple como esto:

```python
def lambda_handler(event, context):
    pokemon_id = event["pokemon_id"]
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/")
    pokemon = json.loads(response.text)
    tweeted = tweet(pokemon)
    return {
        "message": f"It is {pokemon['species']['name']}!",
        "tweeted": tweeted
    }
```

La parte esencial del código de nuestra lambda es la función `lambda_handler` junto con sus dos parámetros `event` y  `context`; a nosotros nos preocupa el primero, que es un diccionario que contiene información que queremos pasar a la lambda cuando se ejecute. En este caso estamos esperando un entero, para el valor de `pokemon_id`. La lambda use este número para obtener un pokémon de la PokeAPI, luego regresa otro diccionario con información "útil". Desde luego, este ejemplo no es tan serio, y tus lambdas podrían realizar tareas más críticas.

A pesar de que nuestro código se está ejecutando en un entorno que no tenemos bajo nuestro control, aún podemos acceder a las variables de entorno del sistema en la que se está ejecutando. La función `tweet` trata de obtener secretos de las variables de entorno que permitirán al código escribir un tweet sobre el pokémon seleccionado:


```python
def  tweet(pokemon):
    variables = [
        "API_KEY",
        "API_SECRET_KEY",
        "ACCESS_TOKEN",
        "ACCESS_TOKEN_SECRET"
    ]

    if  all(var in os.environ for var in variables):
        twitter = Twython(
            os.environ["API_KEY"],
            os.environ["API_SECRET_KEY"],
            os.environ["ACCESS_TOKEN"],
            os.environ["ACCESS_TOKEN_SECRET"]
        )
        twitter.update_status(status=f"It is {pokemon['species']['name']}!")
        return  True
    return  False
```
<small>[Da click aquí](https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/obtaining-user-access-tokens) para aprender más sobre tokens y secretos, sin embargo esto no es necesario para el resto del tutorial.</small>

Ambas funciones, junto con sus `import`s pueden ser colocados en un solo archivo (también puedes organizar mejor tu código), en este caso decidí usar un solo archivo.

### *Packaging*

El siguiente paso es preparar nuestro código para la carga. Si no hubiéramos hecho uso de librerías de terceros, podríamos simplemente poner el código de la lambda en un editor en línea provisto por Amazon; sin embargo, ese no es nuestro caso y tenemos que comprimir nuestro código junto con sus dependencias en un solo archivo.

Hay algo a tomar en cuenta antes de preparar nuestra lambda: es muy probable que el sistema operativo en el que la lambda se va a ejecutar no coincida con el que usamos para desarrollarla. La lambda se ejecuta en una versión de [linux publicada por Amazon](https://aws.amazon.com/amazon-linux-ami/), lo cual significa que puede que algunos de nuestros paquetes no funcionen cuando se esté ejecutando en AWS.

Pero, no te preocupes, que hay una solución fácil y sencilla: Docker! Podemos ejecutar un contenedor con una imagen similar a la que usa Amazon. Si instalamos nuestros paquetes ahí, estos deberían funcionar sin problemas en AWS... después simplemente tenemos que comprimir lo instalado. Para llevar a cabo nuestro plan, ejecutamos el siguiente comando:

```shell
mkdir build
pip freeze > ./build/requirements.txt
cp *.py build
docker run --rm -v ${PWD}/build:/var/task \
    -u 0 lambci/lambda\:build-python3.7 \
    python3.7 -m pip install -t /var/task/ -r /var/task/requirements.txt
cd build && zip -r ../lambda.zip *
```
Para explicar:
 
 - **mkdir build**: creamos una carpeta llamada *build*  
 - **pip freeze > ./build/requirements.txt**: generamos un archivo `requirements.txt` dentro de la carpeta que acabamos de crear, este proviene de nuestro entorno virtual    
 - **cp *.py build**: copiamos el código de nuestra lambda a la carpeta *build*  
 - **docker run ...**: ejecuta el comando `python3.7 -m pip install -t /var/task/ -r /var/task/requirements.txt` dentro del contenedor creado con `lambci/lambda\:build-python3.7` como imagen, este contenedor tiene la carpeta `build` montada como *volume* en la dirección `/var/task/`.  
 - **cd build && zip -r ../lambda.zip \***: para el último paso, comprimimos los archivos de código y los paquetes en el archivo `lambda.zip`

### Cargando nuestra lambda

Una vez que tenemos nuestro zip, lo único que nos queda es configurar nuestra lambda en la consola de AWS, así que inicia sesión y dirígete a la sección de Lambda:

![From the Services tab click the Lambda menu, it is under Compute](https://thepracticaldev.s3.amazonaws.com/i/qpq77qck8r1sfqfjipe3.png)

De ahí verás un botón muy llamativo, que dice "Create a function" o algo similar. Después llena el formulario con el nombre de tu lambda, como *runtime* escoge *Python 3.7*, y recuerda, nuestra lambda es desde cero, o *from scratch*.

![Change the name of your lambda, and select the appropriate runtime](https://thepracticaldev.s3.amazonaws.com/i/gqfnf3z2rd1f0ybmw6ca.png)

La siguiente pantalla muestra la configuración de nuestra lambda, lo que necesitamos hacer ahora es navegar a la sección **Function code**. donde debemos elegir la opción *Upload a .zip file* en el menú *Code entry type. También establece el valor de *Handler* con el valor `lambda_function.lambda_handler` que es en donde se encuentra nuestra función. Ya por último elige el archivo que acabamos de crear y cárgalo:  

![Function code section](https://thepracticaldev.s3.amazonaws.com/i/m6apg8dajp743gort1f3.png)

Da click en el botón *Save* y una vez que se haya guardado, la sección **Function code** cambiará a un editor de código que nosotros no usaremos.

#### Configurando la lambda

Si recuerdas, nuestra lambda puede hacer uso de variables de entorno, para modificarlas a nuestro antojo es necesario navegar a la sección **Environment variables**, en donde tenemos que establecer los valores que usaremos:

![Our environment variables](https://thepracticaldev.s3.amazonaws.com/i/bjhqss38oiqryqjgl9g2.png)

¡No olvides guardar tus cambios a cada rato!

#### Probando nuestra lambda

Ahora sí, ya tenemos casi todo. Si regresas al principio de la página, verás que a un lado del botón *Save*, hay otro que podemos usar para crear eventos de prueba, cuando lo presiones, te dará la oportunidad de crear el mensaje que tu lambda recibirá como prueba:

![Create the test message your lambda will receive](https://thepracticaldev.s3.amazonaws.com/i/4h117l40fu6dlfbg3s64.png)

Después de que lo llenes, puedes guardar y presionar *Test* de nuevo, esta vez la lambda se deberá ejecutar. Puedes ver el resultado de la ejecución en el panel que se muestra. Si configuraste la parte de los tweets, también podrás ver un nuevo tweet en la cuenta que elegiste:

![Logs display](https://thepracticaldev.s3.amazonaws.com/i/dpu6v1zc6ttydkjzazj1.png)

![The tweet we just tweeted from our lambda](https://thepracticaldev.s3.amazonaws.com/i/3okqr3xxu062y9khz9oj.png)

Y eso es todo, ahora ya tienes una lambda que es empacada en el mismo entorno que se va a ejecutar. El código de la lambda se [encuentra en GitHub](https://github.com/messier16/faas)! Espero me hayas podido seguir en este post, y si tienes algún comentario o pregunta, no dudes en hacérmelo llegar ya sea en los comentarios o a mi [cuenta de twitter @io_exception](https://twitter.com/io_exception/).
