---
layout: post
language: es
title: Pruebas unitarias con pytest
date: 2020-05-11 10:00:00
short_summary: Otra entrega de "detrás de los datos", en esta ocasión hablaré sobre cómo podemos asegurarnos de que nuestro código funciona como esperamos usando pytest.
tags: pytest, python, testing
original_url: https://tacosdedatos.com/animaciones-matplotlib
---  

#### Aviso  
A lo largo de este post estaré probando las funciones del código que escribí para el post sobre la [generación automática de datasets](https://tacosdedatos.com/generacion-automatica-datasets); sin embargo no es necesario que leas ese post primero, pero seguramente te ayudará a ponerle más contexto al código que aquí se presenta.

## ¿Qué es *pytest*?  

*pytest* es un *framework* para Python que ofrece la recolección automática de los *tests*, aserciones simples, soporte para *fixtures*, *debugeo* y mucho más... no te preocupes si algunas de estas palabras no te hacen mucho sentido; intentaré aclararlos más adelante a lo largo de este post.

Por cierto, *pytest* no es el unico *framework* disponible; también está *nose*, *doctest*, *testify*... pero *pytest* es el que uso y de el que conozco más.

Para obtener *pytest* lo puedes descargar desde PyPI con tu gestor de paquetes de elección:

```shell
pip install pytest
```

## Escribiendo nuestros *tests*

Para escribir las pruebas es necesario escribir funciones que comiencen con el prefijo `test_`. Es necesario que las llamemos así ya que al momento de ejecutar *pytest* debemos especificar un directorio raíz, a partir de este directorio *pytest* leerá todos los archivos buscando funciones que comiencen con `test_`. Por ejemplo, si miras el [repositorio de *medium-collector*](https://github.com/fferegrino/medium-collector), verás que todos los tests están contenidos dentro de un folder apropiadamente llamado *tests*. Para ejecutar todas las pruebas, lo que tenemos que hacer es ejecutar *pytest* con esta carpeta como argumento:

```shell
pytest tests/
```

## Parametrizando nuestras pruebas  
Comencemos por escribir un test sencillo: una sola entrada, una sola salida. y sin llamadas a servicios externos. Me refiero a una función que toma una cadena codificada (como esta: `=?UTF-8?B?VGhlcmXigJlz?= more to the story`) y regresa otra cadena (como esta: `There’s more to the story`), en este caso estoy hablando sobre la función [`get_subject` method](https://github.com/fferegrino/medium-collector/blob/v0.0.0/medium_collector/download/parser.py#L12):  

```python
def get_subject(subject):
    subject_parts = []
    subjects = email.header.decode_header(subject)
    for content, encoding in subjects:
        try:
            subject_parts.append(content.decode(encoding or "utf8"))
        except:
            subject_parts.append(content)
    return "".join(subject_parts)
```  

Para escribir una prueba unitaria es tan "simple" como hacer esto:  

```python
def test_get_subject():
    expected = "There's more to the story"
    actual = get_subject("=?UTF-8?B?VGhlcmXigJlz?= more to the story")
    assert expected == actual
```

Sin embargo, esta funcion necesita ser probada con el caso en donde toda la cadena está codificada, o el caso en donde no lo está. Para cubrir estos casos tendríamos que escribir métodos como `test_get_subject_all_encoded` y `test_get_subject_none_encoded`, pero eso sería una duplicación absurda de código, para solucionar este problema de **probar el mismo código con multiples valores de entrada** podemos hacer uso de la **parametrización** usando el decorador `@pytest.mark.parametrize`:

```python
import pytest

@pytest.mark.parametrize(
    ["input_subject", "expected"],
    [
        # Input 1
        (
            "=?UTF-8?B?V2hlbiBhICQxMDAsMDAwIFNhbGFyeSBJc27igJl0IEVub3VnaCB8IEFkYW0gUGFyc29ucyBpbiBNYWtpbmcgb2YgYSBNaWxsaW8=?= =?UTF-8?B?bmFpcmU=?=",
            "When a $100,000 Salary Isn’t Enough | Adam Parsons in Making of a Millionaire",
        ),
        # Input 2
        (
            "=?UTF-8?B?VGhlcmXigJlz?= more to the story", 
            "There’s more to the story"
        ),
        # Input 3
        (
            "7 Things Rich People Advise But Never Do | David O. in The Startup",
            "7 Things Rich People Advise But Never Do | David O. in The Startup",
        ),
    ],
)
def test_get_subject(input_subject, expected):
    actual = get_subject(input_subject)
    assert actual == expected
```

El código anterior le indica a *pytest* que ejecute la prueba `test_get_subject` tres veces, cada una reemplazando `input_subject` y `expected` con sus valores correspondientes especificados en el segundo argumento de `parametrize`. 

## Fixtures  
En algunas ocasiones tal vez tengamos **pruebas que comiencen desde cierto estado**, este estado puede ser tener datos en una base de datos, tener archivos en alguna carpeta, o tal vez simplemente tener el objeto correcto como entrada a la función; es ahí donde las *fixtures* son útiles.

Por ejemplo, en el repositorio de *medium-colletor* hay una función llamada `parse_mail` que, como el nombre lo sugiere, podemos usar para extraer información de un objeto de la clase `email.message.Message`. Esta es una versión simplificada de la implementación del método:  

```python
def parse_mail(email_message):
    html = get_html(email_message)
    mail_info = {
        "id": email_message["Message-ID"],
        "to": email_message["To"],
        "from": email_message["From"],
        "subject": get_subject(email_message["Subject"]),
        "date": email_message["Date"],
    }
    return mail_info, html
```  

Para probar esta función necesitamos un objeto de la clase `Message`, pero en realidad no quiero tener que conectarme a nuestro servidor de email cada vez que ejecutemos la prueba; este es el escenario perfecto para usar una *fixture*. Para definir una, tenemos que isar algo como el siguiente código:  

```python  
@pytest.fixture
def dummy_mail():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Link"
    msg["From"] = "you@this.com"
    msg["To"] = "me@that.com"
    msg["Message-ID"] = "123"
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000 (UTC)")
    
    text = "Hi!"
    html = f"<html><head></head><body><p>{text}<br></body></html>"
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    return msg
``` 

Lo primero que hay que notar es que `@pytest.fixture` es usado como decorador de... ¿¡una función!? Sí, así es, una *fixture* no es nada más que una función cuyo valor de retorno debe ser el valor que queremos que esa *fixture* tenga. En este caso, el valor de nuestra *fixture* será un objeto de la clase `MIMEMultipart` que hereda de `Message` que es justo lo que queremos.  

Ahora, para usar nuestra *fixture* llamada `dummy_mail` en nuestra prueba es suficiente con pasarla como argumento en nuestra función de prueba:

```python
def test_parse_mail(dummy_mail):
    expected_mail_info = {
        "id": "ad841b37bd4b9b5403b575432f67f5ed2d68ed40",
        "to": "a4747a50dad63531704f5ab32509bb0c60b7350f",
        "from": "you@this.com",
        "subject": "Link",
        "date": ANY,
    }
    mail_info, decoded = parse_mail(dummy_mail)

    assert mail_info == expected_mail_info
    assert decoded == "<html><head></head><body><p>Hi!<br></body></html>"
```

Cuando ejecutamos *pytest*, este tratará de resolverlas antes de que se ejecute cualquier prueba que las use, y una ves que estas esten listas, los métodos de prueba reciben los valores especificados en cada método asociado. Este mecanismo permite algunos otros usos interesantes de los que hablaré más adelante.  

### Una característica extra de las *fixtures*  
Las *fixtures* de *pytest* son geniales, y otro de sus usos es cuando queremos reutilizar el mismo fragmento de código en dos o más funciones de prueba. Imagina que necesitamos usar un objeto de la clase `Message` para dos pruebas. Podríamos haber declarado una varible global, digamos `MESSAGE = MIMEMultipart("alternative")` y después usarla en nuestros métodos así:

```python
def test_parse_mail_1():
    parse_mail(MESSAGE)
    # ...
    
def test_parse_mail_2():
    parse_mail(MESSAGE)
    # ...
```

Pero en este caso, ambos tests estarían usando la misma variable, `MESSAGE` lo que significa que cualquier cambio hecho por `test_parse_mail_1` afectaría el `MESSAGE` que `test_parse_mail_2` recibe, esto rome el propósito de las pruebas unitarias, ya que nuestros tests no estarían aislados. Sin embargo, cuando usamos *fixtures*, cada función de prueba recibe una copia nueva de lo que sea que regrese nuestra función marcada con `@pytest.fixture`, haciendo fácil y sencillo usarlas una y otra vez.


## Patching  
Sin lugar a dudas, algunas partes de nuestro código dependerán de librerías de terceros o a servicios externos que no queremos ejecutar o contactar cuando ejecutamos nuestras pruebas. Ya sea porque la librería que estamos usando consume muchos recursos o es un sistema productivo que no debería ser tocado durante las pruebas, aquí es cuando el **patching** brilla por su utilidad; este nos ayuda a **reemplazar la el comportamiento (o valores de retorno) de una llamada a una función** con lo que nosotros dispongamos.

Imagina que la función `get_html` contiene código que es muy *"costoso"* ejecutar, y no lo queremos que este código se ejecute cada vez que llamamos al test `test_parse_mail`, entonces podemos *parcharlo* (tengo que decir que el *patching* no es una funcionalidad de *pytest* si no que viene con Python por default).

Hay dos formas de *"parchar"* nuestro código: una de ellas es haciendo uso de la instrucción `with`, pasando el nombre completo de la función que queremos *"parchar"*. Un test que aplica un *patch* a la función `get_html` dentro de `parse_email` se vería así:  

```python
from unittest.mock import patch

def test_parse_mail(dummy_mail):
    expected_mail_info = {
        "id": "ad841b37bd4b9b5403b575432f67f5ed2d68ed40",
        # ...
    }
    
    with patch("medium_collector.download.parser.get_html", 
        return_value="Hello") as patched:
        mail_info, decoded = parse_mail(dummy_mail)

    patched.assert_called_once()
    assert mail_info == expected_mail_info
    assert decoded == "Hello"
```  

En el fragmento anterior estamos *"parchando"* la función y estableciendo el valor de `"Hello"` como su valor de retorno con `return_value`. Esto significa que `"Hello"` será regresado cada vez que la función es ejecutada. Ahora que la función original no es realmente ejecutada; podemos asegurarnos de que esto pase mediante una 

In the previous snippet, we are patching the function and assigning it `"Hello"` as its `return_value`, that is a value that must be returned every that function is called. Now that our function is not called, we can make sure we did call it by asserting it was, each `patch` instance offers a set of methods that make it easy for us to find out whether they were called, how many times they were called, as well as the arguments used to invoke them; for now we check it was called with `assert_called_once`.

### Perils of patching
Patching may look like an easy solution to avoid contacting external services or expensive function calls. However, you must know that you are making some significant assumptions about the code being patched:  
 - You know the expected behaviour of the code being patched (you know what it returns and how it fails). 
 - You can realistically mock any return value of the code being patched. 

When patching be aware that what you are patching may return a complex type that is hard to mimic, and patching it badly may result on you testing against a scenario your code will not find in real life. To overcome this, you may have to examine with detail what are the return values of what you are patching to do it correctly.

Another common problem with patching is that at some point we may get carried over and just end up patching everything... which again, makes up for tests that are not really testing scenarios that your code will not find. If you find yourself doing this, it is probably worth reconsidering if unit testing is the right approach for that specific piece of code, maybe an integration test is better in that case.

## *"Advanced"* fixtures
As mentioned before, the way *pytest* resolves the fixtures can be used to give our code more flexibility. In the *medium-collector* app there is a function that uploads some files to an S3 bucket using the *boto* library, this is the function `upload_files`, which looks somewhat like this:

```python
def upload_files(file, bucket):
    client = boto3.client(
        "s3",
        aws_access_key_id=config("ACCESS_KEY"),
        aws_secret_access_key=config("SECRET_KEY"),
        region_name="eu-west-2",
    )
    client.upload_file(str(file), bucket, file.name)2
```

Of course, I do not want to keep contacting AWS every time I run the tests; here is where the library `moto`  comes to the rescue. In the word of their creators: *"Moto is a library that allows your tests to mock out AWS Services easily."*. The way they suggest you use it is as a context manager:

```python
def test_my_model_save():
    with mock_s3():
        conn = boto3.resource('s3', region_name='us-east-1')
```

To test our function, we need two things before we can actually call `upload_files` test it:

 1. Mock S3; we don't want to talk with AWS in our unit tests,
 2. Have an existing bucket; our code assumes the bucket already exists

To achieve both things with a fixture, we could have something like this:

```python
@pytest.fixture
def bucket():
   return "my_special_bucket"

@pytest.fixture
def mock_storage(bucket):
    @contextmanager
    def inner(create_bucket=True):
        with mock_s3():
            conn = boto3.client("s3", region_name="eu-east-1")
            if create_bucket:
                conn.create_bucket(Bucket=bucket)
            yield
    return inner
```

The fixture is, in reality, a function (`inner`) that thanks to the decorator `contextmanager` acts as a context manager (we can call `with` on it).  In terms of the contents of the function, you can see that we are using `mock_s3` as recommended by the developers of *moto*, inside the context we create a *boto3* client, then, depending on a parameter we create or not a bucket. And lastly, as we are treating this function as a context manager, we `yield`. 

Also, not sure if you noticed it, but `mock_storage` takes in another fixture as an argument (`bucket` in this case). That is another excellent feature of *pytest*, it allows us to create some dependencies within our fixtures, and it solves them for us before executing our tests.

Now, we are ready to test our `upload_files` function with this test:

```python
def test_upload_files(bucket, mock_storage):
    with mock_storage(create_bucket=True):
        upload_files(files_path)
        client = boto3.client("s3", region_name="eu-east-1")
        contents = client.list_objects(Bucket=bucket)["Contents"]
    assert len(contents) == 1
```

## Practice!  

I woud have liked to prepare some sort of notebook or some other interactive environment you could use to play around with the tests, but I firmly believe that, for this topic it is probably better to get your hands on some real code. I encourage you to download the [*medium-collector* repo](https://github.com/fferegrino/medium-collector) app and run the tests.

## Going beyond unit tests  
Even though *pytest* is great for unit testing, nothing stops us from using it for other, more complex, tests such as integration, or even end-to-end tests. With tools like Docker, localstack and other plugins, it is possible to come up with a powerful testing framework for all your Python projects. In a future post I will detail how you can grasp these tools to create a full end-to-end test using *pytest*, so make sure you are following me either here or [at twitter @io_exception](https://twitter.com/io_exception).
