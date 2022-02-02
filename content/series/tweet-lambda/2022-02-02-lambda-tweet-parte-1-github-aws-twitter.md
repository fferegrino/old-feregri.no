---
layout: post
language: es
title: Configurando Twitter y AWS – Bot con AWS Lambda: P1
date: 2022-02-02 10:00:01
short_summary: Vamos a hablar sobre algunos detalles “administrativos” de conseguir y almacenar los secretos necesarios para que esta pequeña aplicación funcione
tags: python, github, aws
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/cycles-part-1_BOlOK42Bl.jpg
slug: lambda-tweet-parte-1-github-aws-twitter
--- 

Esta serie de posts consta de 6 entregas, siendo esta la primera en donde vamos a hablar sobre algunos detalles “administrativos” de conseguir y almacenar los secretos necesarios para que esta pequeña aplicación funcione. Los siguientes posts en la serie abordan a su vez un aspecto muy específico del problema, puedes encontrarlos aquí:

 - Configurando Twitter y AWS - [Parte 1](/lambda-tweet-parte-1-github-aws-twitter)
 - Programando la lambda con Python - [Parte 2](/lambda-tweet-parte-2-python)
 - Mejorando el mapa con GeoPandas - [Parte 3](/lambda-tweet-parte-3-mapas-geopandas)
 - Creando la lambda en un contenedor - [Parte 4](/lambda-tweet-parte-4-contenedor-lambda)
 - Infraestructura con Terraform - [Parte 5](/lambda-tweet-parte-5-terraform)
 - Automatización con GitHub Actions - [Parte 6](/lambda-tweet-parte-6-github-actions)

---

En Londres hay un sistema de renta de bicicletas el cual suelo usar frecuentemente, hay cerca de 700 estaciones en toda la red y desde siempre me intrigó conocer cómo es que estas fluyen en la ciudad.

Resulta que la autoridad a cargo del sistema tiene una API que permite ser consultada para saber cuántas bicicletas hay por estación al momento de realizar esta consulta; y resulta que esta es justo la información necesaria para crear una visualización que me permitiera observar el flujo a lo largo del día.

Así que con eso en mente me decidí crear un bot que consultara el estado de la red, y así es como se ve el resultado final, al que llegaremos cuando esta serie de post esté terminada.

![https://twitter.com/CyclesLondon/status/1488784529766682625](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/Screenshot_2022-02-02_at_22.08.13_Gyqq-QAyJ.png?tr=w-500)

Sí, es un tuit, y es que lo que vamos a hacer es una aplicación que tuitee el estado de la red de bicicletas cada determinado tiempo. En esta serie te voy a hablar de: Python con pandas, geopandas, twython, AWS Lambda, Docker...

# Secretos

Antes de continuar es necesario realizar unas cuantas tareas administrativas. A recordar que lo que vamos a hacer es:

1. Hacer el despliegue de la infraestructura necesaria en AWS de forma programatica – lo cual significa que necesitaremos llaves de acceso
2. Tuitear de forma programática – lo cual significa que necesitaremos llaves de acceso

# AWS

 > 😅 No estoy aún muy seguro de los costos de AWS para este ejercicio, estoy un 80% seguro que los recursos que usaremos caen dentro de el [AWS Free Tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all), pero por si las dudas, checa por tu cuenta.

Las lambdas se ejecutan en AWS, por lo cual requerirás contar con una cuenta de AWS. Hay muchos tutoriales en la web sobre cómo crear una así que no me voy a detener mucho en esto.

El siguiente paso es crear un usuario y darle permisos específicos para las tareas que vamos a realizar. Dentro de tu consola, busca el servicio IAM:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/iam-service_fI9EuukZ5.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/iam-service_fI9EuukZ5.png)

Ahí navega a *Access Management > Users* y da click en el botón *Add users:*

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-user_FIEBF60rO.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-user_FIEBF60rO.png)

Selecciona un nombre para este usuario y algo muy importante, selecciona el checkbox que dice *Access key - Programmatic access* puesto que vamos a acceder de forma programática con este usuario – después, da click en el botón de *Next: Permissions* para asignarle los permisos requeridos:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/create-user_fdIHXYTSK.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643452127899](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/create-user_fdIHXYTSK.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643452127899)

En la pantalla de permisos, selecciona primero la opción de *Attach existing policies directly*, lo cual te dejará seleccionar permisos pre-establecidos, de ellos asegurate de seleccionar los siguientes: *SecretsManagerReadWrite*, *IAMFullAccess*, *AmazonEC2ContainerRegistryFullAccess*, *CloudWatchEventsFullAccess*, *AWSLambda_FullAccess* y *AmazonS3FullAccess*, como se muestra en la imagen:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/attach-existing-policies_Pgo79RhJe.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/attach-existing-policies_Pgo79RhJe.png)

Para terminar, y una vez que hayas elegido todos los permisos que te mencioné, da click en el botón *Next: Tags*, luego en el botón *Next: Review* y finaliza dando click en *Create user*. 

Para terminar, se te va a presentar una pantalla de éxito, en donde hay unos cuantos valores que más vale mantener secretos, **muy, muy secretos**. Yo los redacté en la imagen a continuación:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/access-credentials_UqXADfo3Z.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/access-credentials_UqXADfo3Z.png)

Reitero, manten esos secretos a salvo pero a la mano, los vamos a usar más adelante; y ya que estamos en eso, nosotros nos vamos a estar refiriendo a estos de la siguiente manera: *Access key ID* → `AWS_ACCESS_KEY_ID` y *Secret access key* → `AWS_SECRET_ACCESS_KEY`.

# Twitter

 > 😅 Te recomiendo que te crees una cuenta de tuiter excusiva para esta tarea, a menos que quieras que los tuits salgan de tu cuenta “personal” – cualquier cuenta que uses debe estar verificada mediante tu teléfono celular.

Como vamos a tuitear, necesitamos habilitar nuestra cuenta de desarrollador en [developer.twitter.com](https://developer.twitter.com/), si es que aún no la tienes, en la esquina superior derecha te aparecerá un botón de *Sign Up*:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/sign-up_baa3xthaZ.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/sign-up_baa3xthaZ.png)

Tendrás que llenar unos cuantos formularios, coloca tu información (asegúrate de elegir *Making a bot* en la pregunta de *What's your use case?*), así es como yo llené el mío:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/twitter-form_G0tjxZ6zHqa.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/twitter-form_G0tjxZ6zHqa.png)

Después de aceptar los términos y condiciones y verificar tu cuenta de correo electrónico tu cuenta como *developer* estará activa, ahora puedes regresar a [developer.twitter.com](https://developer.twitter.com/) para por fin, crear tu app y obtener otros cuantos secretos.

En el portal de *developers*, navega a *Projects & Apps* y *scrollea* hasta que aparezca el botón de *+ Add App*, da click en él.

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-app_GpJyadpfC.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-app_GpJyadpfC.png)

La siguiente pantallá nos pedirá un nombre para nuestra app y en cuanto elijamos uno, nos entregará una parte de las credenciales que necesitamos para comenzar a tuitear:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/app-keys_sIO3QWVVY.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/app-keys_sIO3QWVVY.png)

De las llaves presentadas, **guarda muy bien la de API Key y API Key Secret**, las vamos a usar para tuitear desde la Lambda. Ah, y de ahora en adelante vamos a conocer a *API Key* como `TWITTER_API_KEY` y a *API Key Secret* como `TWITTER_API_SECRET`. Para finalizar, en esa pantalla da click en el botón *App Settings.*

Dentro de *App Settings*, haz *scroll* hasta que llegues a la sección de *User Authentication Settings*, y ahí da click en *Set Up.*

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/setup-auth-settings_GPZOXrKXx.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643458519793](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/setup-auth-settings_GPZOXrKXx.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643458519793)

Dentro de esta nueva pantalla selecciona solamente *OAuth 1.0a*, y **en *App Permissions* elige *Read and Write:***

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/Screenshot_2022-01-29_at_12.13.27_Q3RdG2yin.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/Screenshot_2022-01-29_at_12.13.27_Q3RdG2yin.png)

Lo que pongas en el resto de los campos no es tan importante, para las direcciones web que son requeridas puedes poner la dirección de tu blog o simplemente https://www.google.com, no importa este valor.

Ahora regresaremos a la pantalla principal de nuestra app, listos para conseguir el resto de los secretos que necesitamos. Para esto navega a la sección *Keys and tokens*, hacia el fondo de la página hasta encontrar *Authentication tokens* – si te das cuenta, nos indica que el token fue creado con permisos de “solo lectura”, para cambiar esto, elige *Regenerate* y te dará nuevos tokens que, sí, vas a tener que proteger y tener a la mano:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/get-new-tokens_wJmCKerJ8.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/get-new-tokens_wJmCKerJ8.png)

De ahora en adelante vamos a conocer a *Access Token* como `TWITTER_ACCESS_TOKEN` y a *Access Token Secret* como `TWITTER_ACCESS_TOKEN_SECRET`.

Y si te das cuenta, el token ahora dice que fue creado con permisos de lectura y escritura:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/read-write_quTnnmuZSKE.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/read-write_quTnnmuZSKE.png)

Hasta ahora ya deberías tener 6 secretos, 2 de AWS: `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`; y 4 de Twitter: `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN` y `TWITTER_ACCESS_TOKEN_SECRET`. Casi terminamos, falta solo una tarea más.

# De vuelta a AWS

## Secretos

Como no queremos andar por ahí publicando nuestros secretos en público, vamos guardarlos en AWS para que después podamos acceder a ellos durante el despliegue de nuestra lambda sin preocuparnos de tenerlos que escribirlos manualmente.

Desde la consola busca el servicio de *Secrets Manager*:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/secrets-manager_bhLEqjsomrk.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643466700574](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/secrets-manager_bhLEqjsomrk.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643466700574)

Deberías encontrar un botón para agregar un nuevo secreto *Store a new secret*, da click en él, lo cual te llevará a una pantalla en donde deberás agregar los secretos de Twitter, lo primero es selccionar *Other type of secret*, luego en *Key/value pairs* agrega los secretos, solo de Twitter, recuerda que son 4,usa *+ Add row*, para agregar más campos – deja el resto de opciones con su valor por default y da click en *Next*:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-secret_FTpOPzXP2.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643468105533](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-secret_FTpOPzXP2.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643468105533)

La siguiente pantalla te preguntará sobre el nombre de tu secreto, elige algo descriptivo, puedes usar `/` para separar distintos *namespaces* con el fin de hacer más descriptivo el nombre:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/secret-name_Z5HZ5xL_C.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643468898109](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/secret-name_Z5HZ5xL_C.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643468898109)

Si quieres agrega una descripción, deja todos los campos restantes en blanco o con su valor default y da click en *Next* hasta que el botón se convierta en *Store*, el cual también debes *clickear*. 

Al terminar volverás a la pantalla de inicio del *Secrets Manager* y listo, el secreto ha sido guardado.

## Una cubeta para Terraform

Más adelante vamos a usar una herramienta llamada *Terraform* para gestionar la infraestructura necesaria para desplegar nuestra lambda en AWS. Como parte de su funcionamiento, esta herramienta genera un archivo en donde se almacena el estado de la infraestructura.

Si trabajas en equipo, o vas a usar una herramienta de CI/CD (¡como nosotros!) lo recomendable es que este archivo esté disponible para que quien vaya a añadir o modificar la infraestructura pueda acceder a él. Una de las formas sugeridas (y seguras) de compartirlo es a través de una cubeta de *S3* en *AWS* –o similar si estás trabajando con otro provedor–.

Vamos a crear esta cubeta ya que estamos en la consola de AWS, busca S3 dentro de los servicios disponibles:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/s3_IeOgcIO3T.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/s3_IeOgcIO3T.png)

Al darle click, verás un botón titulado *Create bucket*:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/create-bucket_lHGpvOgwJup.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643739021955](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/create-bucket_lHGpvOgwJup.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643739021955)

Se te presentará una pantalla solicitándote el nombre de la cubeta y la región en la que esta debe ser creada, toda mi infraestructura existirá en *eu-west-1*, la tuya podrá ser diferente, solamente asegúrate de que usas la misma consistentemente a lo largo de este tutorial.

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/bucket-name_KjNP6WrIQ.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643739022089](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/bucket-name_KjNP6WrIQ.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643739022089)

Deja todas las demás opciones con sus valores por defecto y termina la creación de la cubeta. 

# GitHub

Estamos haciendo todo esto porque vamos a automatizar el despliegue de nuestra app desde GitHub, es por eso que deberías crear un nuevo repositorio en el cual iremos poniendo nuestro código – y como verás, también nuestros secretos.

No explicaré cómo crear un nuevo repo, pero sí la parte de los secretos. Primero ve a *Settings* en el repositorio recién creado, luego en la barra izquierda selecciona *Secrets* y luego *Actions*. Por último da click en *New repository secret*.

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-secret-screen_QmpIxD-qM.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643788934148](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-secret-screen_QmpIxD-qM.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643788934148)

Acá la cosa es simple, debes elegir un nombre para el secreto y asignarle un valor. Recuerda, debemos guardar ambos secretos de AWS: `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`, uno a la vez. ¡Asegúrate de que no introduzcas espacios innecesarios en los valores!

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-secret_-p9g8DY-R6.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643788933742](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/add-secret_-p9g8DY-R6.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643788933742)

Al finalizar, deberías tener una pantalla muy similar a esta:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/action-secrets_DXxrDG4C8Wz.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643788934008](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/action-secrets_DXxrDG4C8Wz.png?ik-sdk-version=javascript-1.4.3&updatedAt=1643788934008)

Y listo, ahora si ya está casi todo lo “administrativo”.

# Conclusión

No hubo nada de código en esta entrada, más bien un montón de configuración y tareas administrativas necesarias para permitirnos ejecutar despliegue continuo y para poder tuitear desde una Lambda de AWS.

Recuerda que me puedes encontrar en Twitter [en @io_exception](https://twitter.com/io_exception) para preguntarme sobre este post – si es que algo no queda tan claro o encontraste un *typo*. El código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon) 
