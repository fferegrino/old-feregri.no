---
layout: post
language: es
title: Infraestructura con Terraform – Bot con AWS Lambda: P5
date: 2022-02-02 10:00:05
short_summary: Vamos a generar la infraestructura necesaria para la lambda, incluyendo un repositorio de ECR y Eventos de CloudWatch para llamar a la ejecución de la función
tags: python, github, aws, terraform, ecr, lambda
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/cycles-part-5_FE8AgrAJ6.jpg
slug: lambda-tweet-parte-5-terraform
--- 

Esta serie de posts consta de 8 entregas, siendo esta la quinta en donde vamos a generar la infraestructura necesaria para la lambda, incluyendo un repositorio de ECR y Eventos de CloudWatch para llamar a la ejecución de la función. Los otros posts en la serie abordan a su vez un aspecto muy específico del problema, puedes encontrarlos aquí:

 - Configurando Twitter y AWS - [Parte 1](/lambda-tweet-parte-1-github-aws-twitter)
 - Programando la lambda con Python - [Parte 2](/lambda-tweet-parte-2-python)
 - Mejorando el mapa con GeoPandas - [Parte 3](/lambda-tweet-parte-3-mapas-geopandas)
 - Creando la lambda en un contenedor - [Parte 4](/lambda-tweet-parte-4-contenedor-lambda)
 - Infraestructura con Terraform - [Parte 5](/lambda-tweet-parte-5-terraform)
 - Automatización con GitHub Actions - [Parte 6](/lambda-tweet-parte-6-github-actions)
 - Agregando pruebas con Pytest - [Parte 7](/lambda-tweet-parte-7-add-testing)
 - Optimizando Docker - [Parte 8](/lambda-tweet-parte-8-aligerando-docker)

---

Como ya lo he mencionado anteriormente, estaremos trabajando con una *lambda* de AWS, lo cual significa que tenemos que crear infraestructura en AWS.

Como programador me gusta definir todo en código, sin embargo el aprovisionamiento de infraestructura es algo que hasta hace poco era necesario administrar manualmente – ya sea a través de una interfaz gráfica o una herramienta de consola con posibilidad limitada de *scripting*.

A lo largo de los años han surgido herramientas que nos acercaban más al sueño de poder crear infraestructura tan solo definiendo cómo es que esta debe ser de forma escrita, herramientas como Ansible, CloudFormation y Terraform permiten hacer justamente eso. Y es justamente la última que yo elegí para crear los elementos necesarios para esta serie de *posts*.

No es mi interés explicarte cómo es que Terraform funciona (ni yo mismo sé bien, en este post hice lo mínimo para que la *lambda* funcionara). La forma en la que presento este post es describiendo el contenido del archivo *terraform/main.tf* que contendrá la infraestructura.

# Proveedores – *Providers*

Terraform interactúa con sistemas remotos (como AWS) a través de *plugins*; estos *plugins* son conocidos como proveedores o `providers`.

Cada módulo de terraform debe especificar los "proveedores" que necesita a través de el bloque `required_providers`, cada proveedor tiene un nombre, una ubicación y una versión. Por ejemplo, en el ejemplo de la lambda que voy a publicar estoy usando 2 proveedores:

- `aws`, que se ubica en `hashicorp/aws` en cualquier versión `3.27.X`
- `null`, que es un proveedor "especial" del cual les hablaré  más adelante.

```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }

    null = {
      version = "~> 3.0.0"
    }
  }
  required_version = ">= 0.14.9"

  backend "s3" {
    bucket = "feregrino-terraform-states"
    key    = "lambda-cycles-final"
    region = "eu-west-1"
  }
}
```

## Configuración de *backends*

Dentro del bloque de configuración de *terraform* también puedes ver que existe otro bloque definido como `backend "s3"`, este bloque nos ayuda a especificar en dónde se localizará el archivo de estado en donde se preservará el estado de la infraestructura que hemos creado con *terraform* hasta el momento. Como lo discutí en el primer post de la serie, este archivo existirá en una cubeta de *S3*, cuya especificación colocamos en el bloque *backend*.

## Configuración de proveedores

Algunos proveedores requieren configuración extra, por ejemplo, AWS requiere configurar cosas como la región a la que nos queremos conectar, el perfil y las credenciales que vamos a usar. Aunque la recomendación es que no pongas passwords ni secretos en código, por ejemplo, en la configuración de AWS yo tengo:

```
provider "aws" {
  profile = "default"
  region  = "eu-west-1"
}
```

# Fuentes de datos – *Data Sources*

Terraform nos permite acceder a datos definidos fuera de nuestros archivos de configuración, a través de bloques `data`, a través de estos podemos acceder a información sobre el usuario que está ejecutando comandos en AWS, usando `aws_caller_identity`:

```
data "aws_caller_identity" "current_identity" {}
```

# Valores locales – *Local Values*

[https://www.terraform.io/language/values/locals](https://www.terraform.io/language/values/locals)

Me gusta pensar en valores locales como variables dentro de cada módulo, y las debemos definir dentro de un bloque `locals`, locals también puede tomar valores de otras fuentes, como variables o *data sources* para simplificar el acceso a ellas:

```
locals {
  account_id          = data.aws_caller_identity.current_identity.account_id
  prefix              = "lambda-cycles-final"
  ecr_repository_name = "${local.prefix}-image-repo"
  region              = "eu-west-1"
  ecr_image_tag       = "latest"
}
```

# AWS

## Secretos

Dada la naturaleza del servicio que estoy tratando de desplegar, es necesario acceder a los secretos almacenados en el gestor de secretos de AWS, estos deben ser especificados como fuentes de datos, con bloques `data` , en el caso de los secretos, es necesario acceder al secreto con `aws_secretsmanager_secret` y luego a la última version de este con `aws_secretsmanager_secret_version`:

```
data "aws_secretsmanager_secret" "twitter_secrets" {
  arn = "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:lambda/cycles/twitter-2GMvKu"
}

data "aws_secretsmanager_secret_version" "current_twitter_secrets" {
  secret_id = data.aws_secretsmanager_secret.twitter_secrets.id
}
```

## Repositorio de ECR

Como la lambda va a ser desplegada usando un contenedor de docker es necesario crear un repositorio en ECR, podemos usar el recurso `aws_ecr_repository` especificando el nombre del repositorio a partir de una de las variables locales:

```
resource "aws_ecr_repository" "lambda_image" {
  name                 = local.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}
```

## Creando una imagen de Docker

[https://www.terraform.io/language/resources/provisioners/local-exec](https://www.terraform.io/language/resources/provisioners/local-exec)

Una vez creado el repositorio es necesario cargar una imagen en él, sin embargo Terraform es usado para definir infraestructura, no para realizar tareas como construir una imagen de docker ni mucho menos cargarla. Voy a suponer que para este paso, antes de ejecutar el Terraform ya tengo una imagen construida con el nombre de `lambda-cycles` lo único que faltaría entonces es cargarla al repositorio de ECR.

Podemos usar un pequeño *hack* para conseguir esto con Terraform usando un *recurso nulo* (`null_resource`) y un proveedor llamado `local-exec` que permite especificar comandos para que se ejecuten en la computadora local:

```
resource "null_resource" "ecr_image" {
  triggers = {
    python_file_1 = filemd5("../app.py")
    python_file_2 = filemd5("../plot.py")
    python_file_3 = filemd5("../tweeter.py")
    python_file_4 = filemd5("../download.py")
    requirements  = filemd5("../requirements.txt")
    docker_file   = filemd5("../Dockerfile")
  }
  provisioner "local-exec" {
    command = <<EOF
           aws ecr get-login-password --region ${local.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${local.region}.amazonaws.com
           docker tag lambda-cycles ${aws_ecr_repository.lambda_image.repository_url}:${local.ecr_image_tag}
           docker push ${aws_ecr_repository.lambda_image.repository_url}:${local.ecr_image_tag}
       EOF
  }
}
```

¿Notaste el bloque `triggers`? este bloque nos ayudará a rastrear los cambios a los archivos que determinan si el contenedor de la *lambda* a cambiado, con `filemd5` obtenemos un hash de los archivos especificados, esto haría que cualquier cambio a los archivos *.py*, los requerimientos o el *Dockerfile* causarán que la imagen sea vuelta a cargar a su repositorio de ECR.

## Información de la imagen

Es necesario generar una fuente de datos (con la forma de una `aws_ecr_image`) que especifique una dependencia a la creación y publicación de la imagen, esto lo podemos hacer gracias a `depends_on`:

```
data "aws_ecr_image" "lambda_image" {
  depends_on = [
    null_resource.ecr_image
  ]
  repository_name = local.ecr_repository_name
  image_tag       = local.ecr_image_tag
}
```

## Políticas y permisos – *Policies* and *permissions*

Antes de crear la *lambda*, tengo que encargarme de otras tareas administrativas, la primera es crear un rol para la que la *lambda* pueda asumir y ser ejecutada:

```
resource "aws_iam_role" "lambda" {
  name               = "${local.prefix}-lambda-role"
  assume_role_policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Action": "sts:AssumeRole",
           "Principal": {
               "Service": "lambda.amazonaws.com"
           },
           "Effect": "Allow"
       }
   ]
}
 EOF
}
```

Ahora, como quiero monitorear mi lambda, para saber si ocurrió algún error durante su ejecución, es necesario otorgarle permisos para que pueda crear logs en CloudWatch:

```
data "aws_iam_policy_document" "lambda" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect    = "Allow"
    resources = ["*"]
    sid       = "CreateCloudWatchLogs"
  }
}

resource "aws_iam_policy" "lambda" {
  name   = "${local.prefix}-lambda-policy"
  path   = "/"
  policy = data.aws_iam_policy_document.lambda.json
}
```

## Lambda – por fin

Ahora que ya tengo casi todo en su lugar, puedo crear la lambda a través del recurso `aws_lambda_function`, este es una de las definiciones un poco más densas del documento, así que trataré de explicarlo un poco más a detalle:

Lo primero que hago es añadir una dependencia a la creación de mi imagen en docker con `depends_on`, luego especifico el nombre de la lambda y el rol que debe asumir con `function_name` y `role`. Se de antemano que esta lambda puede tomar un poco de tiempo así que le dejo un `timeout` un poco amplio.

Una vez que creamos nuestra imagen en ECR debemos especificarle a la lambda que el `package_type` es una imagen, seguido de la `image_uri` para que sepa en donde encontrarla.

Para terminar, como mi lambda va a enviar un Tweet es necesario pasarle los secretos necesarios, de nuevo, en el interés de mantener todo de la forma más privada posible habrá que definirlos como variables de entorno (en lugar de *hardcodearlos*); esto lo logro a partir del bloque `environment` y extrayendo los secretos de –valga la redundancia– los secretos previamente almacenados en AWS:

```
resource "aws_lambda_function" "lambda" {
  depends_on = [
    null_resource.ecr_image
  ]
  function_name = "${local.prefix}-lambda"
  role          = aws_iam_role.lambda.arn
  timeout       = 300
  image_uri     = "${aws_ecr_repository.lambda_image.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type  = "Image"
  environment {
    variables = {
      API_KEY             = jsondecode(data.aws_secretsmanager_secret_version.current_twitter_secrets.secret_string)["API_KEY"]
      API_SECRET          = jsondecode(data.aws_secretsmanager_secret_version.current_twitter_secrets.secret_string)["API_SECRET"]
      ACCESS_TOKEN        = jsondecode(data.aws_secretsmanager_secret_version.current_twitter_secrets.secret_string)["ACCESS_TOKEN"]
      ACCESS_TOKEN_SECRET = jsondecode(data.aws_secretsmanager_secret_version.current_twitter_secrets.secret_string)["ACCESS_TOKEN_SECRET"]
    }
  }
}
```

### Ejecutando cada X minutos

Hasta aquí todo bien, si ejecutamos terraform hasta este punto, verás que ya tenemos varias cosas creadas: un repositorio de ECR, una imagen de docker, y una lambda. Pero falta la cereza en el pastel, y es que el punto de convertir el código en una lambda es que quiero ejecutarla varias veces a lo largo del día, cada cierto tiempo. 

Para lograr esta tarea puedo usar un *trigger* con el servicio CloudWatch de AWS, algo que ejecute mi lambda a intervalos de tiempo definidos por mi, esto es posible con Terraform también. 

Lo primero es definir una regla de eventos en CloudWatch:

```
resource "aws_cloudwatch_event_rule" "every_x_minutes" {
  name                = "${local.prefix}-event-rule-lambda"
  description         = "Fires every 20 minutes"
  schedule_expression = "cron(0/20 * * * ? *)"
}
```

Este evento necesita un objetivo, en este caso es mi lambda:

```
resource "aws_cloudwatch_event_target" "trigger_every_x_minutes" {
  rule      = aws_cloudwatch_event_rule.every_x_minutes.name
  target_id = "lambda"
  arn       = aws_lambda_function.lambda.arn
}
```

Y claro, como casi todo en AWS, también necesitamos otorgarle permisos para que el evento pueda invocar la lambda:

```
resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_x_minutes.arn
}
```

***et voilà !*** – tenemos ya todos los ingredientes necesarios para ejecutar y crear nuestra lambda usando Terraform.

Recuerda, todo este contenido existe en el archivo *terraform/main.tf* dentro del repositorio en el que hemos estado trabajando.

Así es como [se ve el repositorio](https://github.com/fferegrino/tweeting-cycles-lambda/tree/part-4-terraform) al terminar este post.

Recuerda que me puedes encontrar en Twitter [en @io_exception](https://twitter.com/io_exception) para preguntarme sobre este post – si es que algo no queda tan claro o encontraste un *typo*. El código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon) 
