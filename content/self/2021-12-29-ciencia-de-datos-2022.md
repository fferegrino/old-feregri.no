---
layout: post
language: es
title: ¿Comenzando con la ciencia de datos 2022?
date: 2021-12-28 10:00:00
short_summary: En este post recopilo algunos de los consejos que te doy para que comiences en la ciencia de datos, inspirado por el hilo de Xavier Carrera en Twitter.
social_image: https://ik.imagekit.io/thatcsharpguy/posts/pillars-ds.jpg?updatedAt=1640723076369&tr=w-1200,h-630,fo-top
tags: data-science
---  

Si tienes como propósito acercarte a la ciencia de datos en este 2022 hice una recopilación de pensamientos (unos que ya había descrito anteriormente) y otros que apenas pongo por escrito. Aquí te ofrezco unos cuantos consejos y recursos desde mi experiencia personal que espero sean de ayuda para la tuya.

 > 👀 Inspirado en el [hilo de Xavier Carrera](https://twitter.com/XaviGrowth/status/1475590298835292163): “Si tuviera que aprender Data Science desde 0 otra vez en 2022, eso es lo que haría", te recomiendo que también le eches un ojo a su Tweet porque vale mucho mucho la pena.

# Conoce qué clase de trabajos en datos hay

Lo primero es lo primero, hay muchas clases de *data scientist*, en la actualidad el famoso unicornio es difícil de encontrar, y muchas compañías ya buscan gente muy especializada: hay puestos enfocados a la investigación, otras orientadas a hacer productos internos, otras a interactuar con la clientela final, otras dedicadas a ventas... tata de investigar las responsabilidades que cada posición que te encuentres conlleva, todo esto para que te vayas formando una idea de qué áreas debes reforzar en lugar de preocuparte por aprender de todo.

 > Yo ya hice un video sobre [las diferentes profesiones que existen al rededor del término "data"](https://www.youtube.com/watch?v=71QtbxZInCM)

## Todos los caminos llevan a Roma

Debes saber que hacer *machine learning* no solo es el único propósito de la ciencia de datos, también espacio para el análisis, visualización, consulta y un montón más de tareas que forman parte de este término sombrilla. No te apures si de entrada no le entiendes al ML, intenta con algo más cercano a lo que estás haciendo actualmente. 

# No te preocupes por aprender cada detalle de todo

La investigación en la ciencia de datos se mueve muchísimo, hay papers nuevos a cada rato, Google, Facebook, Microsoft y similares parecieran crear cosas diario; el estar bombardeado constantemente con nuevos avances puede hacerte perder perspectiva de hacia donde debes dirigir tu carrera y saturare de información entretenida pero irrelevante en muchas veces.

Mi sugerencia es que, una vez que tengas unas bases sólidas, trates de resolver un problema (ya sea laboral o personal) usando lo que tienes a la mano y a partir de ahí estudies lo necesario para completarlo.

Sí, sigue fervientemente las noticias sobre los últimos desarrollos (por Twitter o en *newsletters,* yo trato de leer al menos un artículo por día), pero tampoco te desvivas por implementarlos inmediatamente porque es muy desgastante y a final de cuentas te van a distraer de lograr implementar una solución que funciona para tu organización.

# No te enfoques entornos de desarrollo

Que si debes usar Conda, miniconda, venv, pipenv, poetry; que si instalar Python es una pesadilla; que si necesitas compilar TensorFlow para tu sistema operativo o si tienes conflictos en dependencias. Que si uso PyCharm o VSCode. Que si necesitas comprar una supercomputadora con GPU integrado, o si es mejor ponerle 32Gb de RAM, o un terabyte de disco duro...

La verdad es que enfrentarte a esos problemas cuando vas comenzando lo único que va a conseguir es hacerte perder valioso tiempo que podrías haber pasado practicando; y ni hablar de lo frustrante que puede llegar a ser poner en funcionamiento un entorno.

Como tal te digo **no te preocupes por montar el ambiente de desarrollo perfecto**, para comenzar puedes usar alternativas gratuitas que ya están configuradas para ti, por ejemplo: Los [Notebooks de Kaggle](https://www.kaggle.com/code), los notebooks de [Google Colab](https://colab.research.google.com/) y el más reciente [AWS StudioLab](https://studiolab.sagemaker.aws/).

 > Ahora, si quieres saber sobre entornos virtuales en Python, tengo [un video al respecto](https://www.youtube.com/watch?v=GM-RcOaGN4w). 

# No te preocupes tanto por las matemáticas

Sí, el aprendizaje automático no es más que matemáticas aplicadas, estadística y probabilidad. Sin embargo, esto **no significa que debas ser un experto o experta en matemáticas para poder comenzar**. En mi opinión basta con que sepas cómo es que los principales modelos y algoritmos funcionan para que puedas comenzar a usarlos, que sepas cuáles son sus principales hiperparámetros y cómo es que afectan el desempeño, igualmente debes tener una noción de qué es lo que hace cada uno: calcular distancias entre puntos, buscar un mínimo, multiplicar las variables de entrada por coeficientes... todo de forma coloquial sin entrar a muchos detalles matemáticos.

Llegará un momento en el que tengas que adentrarte a investigar más a detalle el funcionamiento interno de un modelo, para poder identificar qué es lo que podría estar saliendo mal o simplemente para tratar de mejorar tus resultados, pero esto vendrá acompañado de una necesidad o curiosidad una vez que busques incrementar tu conocimiento.

Habiendo dicho esto, no creas que con conocer las APIs de SciKit-Learn es suficiente, si bien los frameworks hacen el programar para machine learning sea muy sencillo, no debes confundir el llamar simplemente a `.fit` con crear un modelo que va a funcionar en producción.

 > Por si te lo perdiste, también hice [un video sobre este tema](https://www.youtube.com/watch=rceZhveizdM).

# No desestimes escribir código limpio y estructurado desde el inicio

Los *data scientist* solían tener fama de escribir código que funcione sin importar a qué grado de limpieza tenga este. Déjame decirte que esos días han quedado atrás. Ojo que con esto no quiero decir que te debes volver un *master* en escribir código limpio, ni que debes convertirte en *software developer*.

**Evita nombres de variables y funciones indescifrables**: nada de `my_function`, `foo` o `frame`, e inclusive esa `i` de tu ciclo *for* también debe tener un mejor nombre, que seas novato escribiendo código no justifica que seas novato comunicándote, y el código es solo otra forma de comunicación. 

También **trata de estructurar tu código en bloques lógicos**, uno en el que solo hagas lectura de datos, otro en donde hagas el *feature engineering,* otro para *feature selection*, modelado y así sucesivamente. No mezcles lectura de datos con el entrenamiento de un modelo de ML.

 > Tengo un video sobre [cómo te recomiendo a ti, *data scientist*, que escribas tu código](https://www.youtube.com/watch=B8Ppy4RgHBg).

# No todo es Python

Podrás impresionarte con los más grandes avances de GPT, las Alexas y los Google Asistants... pero la verdad es que la gran mayoría de la ciencia de datos que existe en la industria poco tienen que ver con datos no estructurados, como *data scientist* te tocará lidiar con datos en forma tabular (puras tablas, pues).

El lenguaje por excelencia para manipular este tipo de información es SQL, por lo tanto es importante que lo aprendas y lo domines hasta cierto nivel. No, **no es necesario que te vuelvas todo un DBA, pero si que sepas construir *queries*** para obtener, filtrar y transformar de forma eficiente los datos que necesitas antes de que te pongas a procesarlos con otros lenguajes.

Puede que tengas la idea de que SQL es algo viejo, que solo se usa en sistemas transaccionales, pero no, SQL es más relevante puesto que para extraer información de los *data warehouses* de tu compañía tienes que usar este lenguaje (o alguno extremadamente similar).

 > Conoce [Snowflake, y cómo es que potencia con SQL las aplicaciones actuales de datos](https://www.youtube.com/watch=TTxJ7kehgRU):

## ¿Excel?

Otra cosa es que mucha gente menosprecia Excel (o cualquier otra hoja de cálculo) cuando hay veces en que es la mejor herramienta para comunicar datos entre personas técnicas y no técnicas: no todos saben usar Pandas para leer un CSV. 

Pero no solo eso, las hojas de cálculo son muy poderosas y bien usadas pueden formar parte de un ciclo inicial de exploración de datos porque no te tienes que estar peleando con visualizar todo en un par de celdas de un Notebook.

# No todo es Python (otra vez)

Como *data scientist* en algún momento vas a tener que explicarle a alguien el por qué tu modelo es mejor, por qué va a funcionar cuando se ponga en producción, por qué usaste ciertas variables pero otras no... 

Es un tanto difícil que alguien pueda entender tus intenciones con solo leer tu código (ya sea en Python o SQL), vas a tener que explicar el producto de ti código. Y no, no quiere decir que si tienes una personalidad introvertida tus posibilidades de ser *data scientist* desaparecen, sino que **debes esforzarte un poco más en poder explicar, tanto técnica, como coloquialmente el por qué de tu código y presunciones sobre los datos que estás usando**.

**No inviertas todo tu tiempo en el código, sino también dedícale algo a la explicación de los resultados que este produce**.

![Pilares de la ciencia de datos](https://ik.imagekit.io/thatcsharpguy/posts/pillars-ds.jpg?updatedAt=1640723076369&tr=w-1200,h-630,fo-top)