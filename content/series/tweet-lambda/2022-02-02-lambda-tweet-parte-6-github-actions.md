---
layout: post
language: es
title: Configurando GitHub Actions – Bot con AWS Lambda: P6
date: 2022-02-02 10:00:06
short_summary: Vamos a usar GitHub actions para automatizar el provisionamiento de recursos con Terraform y la publicación de nuevas versiones de nuestra lambda.
tags: python, github, aws, terraform, github actions
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/cycles-part-6_DbKr-mcvk.jpg
slug: lambda-tweet-parte-6-github-actions
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

Viene la parte de la automatización en GitHub – a través de un *pipeline* de CI/CD, lo primero que vamos a hacer es crear un archivo llamado *aws.yml* en la carpeta .*github/workflows*, como la extensión lo sugiere es un archivo que sigue el formato YAML.

Lo primero que vamos a especificar es el nombre del *pipeline* y las condiciones bajo las que se debe ejecutar:

```yaml
name: Build and deploy lambda-cycles image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
# Job definitions
```

Por el momento quiero que el *pipeline* se ejecute cada vez que alguien pone algo en *main* y cada vez que alguien abre una *pull request* hacia *main.*

Lo siguiente es definir los *jobs* que forman parte del flujo de trabajo – en este caso tendremos dos: uno para preparar nuestra aplicación y la otra para publicarla.

# Preparar la imagen – *build*

Para definir un trabajo debemos especificar los pasos (*steps*) que lo forman, individualmente puedes especificar un nombre más amigable y el tipo de *runner* en el que se ejecuta. Nosotros no usaremos nada complicado, así que `ubuntu-latest` nos funciona bien.

```yaml
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
```

El siguiente paso es especificar los pasos (*o steps,* valga la redundancia) que forman parte de este *job.*

## Pasos

Necesitamos obtener una copia de nuestro código recién *pusheado* a main, usamos la *action* *checkout:*

```yaml
    - name: Checkout
      uses: actions/checkout@v2
```

Como vamos a interactuar con AWS necesitamos configurar las credenciales en el *runner*, Amazon mantiene una *action* para esto, lo que debemos especificar son nuestras credenciales (que previamente establecimos como secretos en nuestro *repo*).

```yaml
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: eu-west-1
```

Este par de pasos es solo para mi implementación, y es que estoy usando *pipenv*, así que toca instalar Python, luego *pipenv* e instalamos las dependencias:

```yaml
    - name: Set up Python 3.8
      uses: actions/setup-python@v1
      with:
        python-version: 3.8

    - name: Install pipenv
      run: |
        pip install pipenv
        pipenv install
```

Los siguientes tres pasos tienen que ver con la creación de la imagen que usaremos para crear la instancia de nuestra *lambda*. 

El primer paso llama a `make container`, la utilidad que añadí en en posts pasados para construir una imagen con la etiqueta `lambda-cycles`. El segundo paso exporta esta imagen a un archivo comprimido. El tercer paso almacena la imagen de *Docker* recién exportada como un artefacto, y es que la usaremos en el siguiente *job*, el del despliegue.

```yaml
    - name: Build lambda-cycles image
      run: make container

    - name: Pack docker image
      run: docker save lambda-cycles > ./lambda-cycles.tar

    - name: Temporarily save Docker image and dependencies
      uses: actions/upload-artifact@v2
      with:
        name: lambda-cycles-build
        path: |
          ./shapefiles/
          ./requirements.txt
          ./lambda-cycles.tar
        retention-days: 1
```

Debemos configurar, inicializar y por último planear la creación de la infraestructura en *terraform*, para lo primero, Hashicorp también nos ofrece una acción pre-definida, para las siguientes dos tareas con que ejecutemos la herramienta de consola *terraform* basta:

```yaml
    - name: Set up terraform
      uses: hashicorp/setup-terraform@v1

    - name: Terraform init
      run: terraform -chdir=terraform init

    - name: Terraform plan
      run: terraform -chdir=terraform plan
```

# Crear infraestructura en AWS

Una vez que GitHub Actions terminó el trabajo *build*, podemos seguir con el de *deploy*. Para definir este trabajo (además de la información de nombre y *runner*) le indico que depende del trabajo `build` y muy importante, que solo debe ejecutarse cuando la rama que va a ejecutar este trabajo es la rama `main`, ojo a la instrucción `if`.

```yaml
	deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'

    steps:
```

## Pasos

Lo de siempre, obtenemos una copia del código con `actions/checkout@v2`:

```yaml
    - name: Checkout
      uses: actions/checkout@v2
```

Volvemos a configurar nuestras credenciales, recuerda que cada trabajo se ejecuta en un *runner* diferente:

```yaml
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: eu-west-1
```

¿Recuerdas que en el *job* anterior creamos un artefacto llamado `lambda-cycles-build` que contenía una imagen de Docker y unas dependencias más? – pues ahora vamos a descargarlo, y después de eso usaremos `docker load` para importar la imagen y que esté disponible para ser usada por *docker.*

```yaml
    - name: Retrieve saved Docker image
      uses: actions/download-artifact@v2
      with:
        name: lambda-cycles-build
        path: ./

    - name: Docker load
      run: docker load < ./lambda-cycles.tar
```

Nuevamente configuramos *terraform*, lo inicializamos y por último aplicamos los cambios, fíjate que estamos usando la opción `-auto-approve` para que los cambios sean aprobados automáticamente sin necesidad de interacción humana.

```yaml
    - name: Set up terraform
      uses: hashicorp/setup-terraform@v1

    - name: Terraform init
      run: terraform -chdir=terraform init

    - name: Terraform apply
      run: terraform -chdir=terraform apply -auto-approve
```

Así es como [se ve el repositorio](https://github.com/fferegrino/tweeting-cycles-lambda/tree/part-5-github-action) al terminar este post.

Recuerda que me puedes encontrar en Twitter [en @io_exception](https://twitter.com/io_exception) para preguntarme sobre este post – si es que algo no queda tan claro o encontraste un *typo*. El código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon) 
