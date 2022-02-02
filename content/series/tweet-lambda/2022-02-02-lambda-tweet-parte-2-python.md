---
layout: post
language: es
title: Programando la lambda con Python – Bot con AWS Lambda: P2
date: 2022-02-02 10:00:02
short_summary: Vamos realizar la implementación en Python para consutar una API, generar un mapa con GeoPandas y tuitear con Twython
tags: python, github, aws
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/cycles-part-2_AXPvmxNGH.jpg
slug: lambda-tweet-parte-2-python
--- 

Esta serie de posts consta de 6 entregas, siendo esta la segunda en donde vamos realizar la implementación en Python para consutar una API, generar un mapa con GeoPandas y tuitear con Twython. Los otros posts en la serie abordan a su vez un aspecto muy específico del problema, puedes encontrarlos aquí:

 - Configurando Twitter y AWS - [Parte 1](/lambda-tweet-parte-1-github-aws-twitter)
 - Programando la lambda con Python - [Parte 2](/lambda-tweet-parte-2-python)
 - Mejorando el mapa con GeoPandas - [Parte 3](/lambda-tweet-parte-3-mapas-geopandas)
 - Creando la lambda en un contenedor - [Parte 4](/lambda-tweet-parte-4-contenedor-lambda)
 - Infraestructura con Terraform - [Parte 5](/lambda-tweet-parte-5-terraform)
 - Automatización con GitHub Actions - [Parte 6](/lambda-tweet-parte-6-github-actions)

---

 > ⚠️ A mi me gusta usar Pipenv para gestionar dependencias y entornos virtuales para aplicaciones en Python – tu puedes usar cualquier otro gestor de dependencias que más te convenga.

Las bibliotecas que voy a utilizar son:

- geopandas
- matplotlib
- mind-the-gap
- pandas
- seaborn
- twython

# Obteniendo la información

Lo primero que necesito hacer es descargar la información de las estaciones de bicicletas de Londres, para ello usaré la biblioteca que yo mismo cree (les puedo platicar de esta en el futuro) para consultar la API de TFL, me cree un archivo separado para poder modularizar la información. La forma en la que lo podemos hacer con `mind-the-gap` es:

```python
from tfl.api import bike_point

all_bike_points = bike_point.all()

# Ahora podemos tomar un elemento y ver su contenido
place = all_bike_points[0]
print(f"{place.commonName} (LAT: {place.lat}, LON: {place.lon})")
# out: Vicarage Gate, Kensington (LAT: 51.504723, LON: -0.192538)
```

Adicionalmente, cada uno de esos elementos como place contienen un conjunto de propiedades adicionales, o `AdditionalProperties` de las cuales podemos extraer información tal como la cantidad de *docks* disponibles, cuántos de estos *docks* están en uso y cuántas bicicletas tiene disponible. Para extraer esta información adicional cree esta función auxiliar:

```python
def get_number(additional_properties: List[AdditionalProperties], key: str) -> int:
    [nb] = [prop.value for prop in additional_properties if prop.key == key]
    return int(nb)

# Y la podemos usar así:
bikes = get_number(place.additionalProperties, "NbBikes")
empty_docks = get_number(place.additionalProperties, "NbEmptyDocks")
docks = get_number(place.additionalProperties, "NbDocks")

print(f"{place.commonName} tiene {bikes} bicicletas disponibles y {docks} docks en total")
# out: Vicarage Gate, Kensington tiene 3 bicicletas disponibles y 18 docks en total
```

A final de cuentas, puedo crear un *data frame* con un ciclo *for*:

```python
def download_cycles_info() -> pd.DataFrame:
    all_bike_points = bike_point.all()
    query_time = datetime.now()
    data = []

    for place in all_bike_points:
        bikes = get_number(place.additionalProperties,"NbBikes")
        empty_docks = get_number(place.additionalProperties,"NbEmptyDocks")
        docks = get_number(place.additionalProperties,"NbDocks")
        data.append(
            (
								place.id, place.commonName,
                place.lat, place.lon,
                bikes, empty_docks, docks,
            )
        )

    data_df = pd.DataFrame(
        data, columns=["id","name","lat","lon","bikes","empty_docks","docks"]
    ).set_index("id")
    data_df["query_time"] = pd.to_datetime(query_time).floor("Min")
		data_df["proportion"] = (data_df["docks"] - data_df["empty_docks"]) / data_df["docks"]

    return data_df

bike_info_data_frame = download_cycles_info()
bike_info_data_frame.head()
```

```python
| id             | name                      |     lat |       lon |   bikes |   empty_docks |   docks | query_time          |   proportion |
|:---------------|:--------------------------|--------:|----------:|--------:|--------------:|--------:|:--------------------|-------------:|
| BikePoints_103 | Vicarage Gate, Kensingt   | 51.5047 | -0.192538 |       1 |            17 |      18 | 2022-01-28 16:18:00 |    0.0555556 |
| BikePoints_105 | Westbourne Grove, Baysw   | 51.5155 | -0.19024  |      14 |            11 |      26 | 2022-01-28 16:18:00 |    0.576923  |
| BikePoints_106 | Woodstock Street, Mayfa   | 51.5141 | -0.147301 |      13 |             8 |      21 | 2022-01-28 16:18:00 |    0.619048  |
| BikePoints_107 | Finsbury Leisure Centre's | 51.526  | -0.096317 |       8 |            12 |      20 | 2022-01-28 16:18:00 |    0.4       |
| BikePoints_108 | Abbey Orchard Street, W   | 51.4981 | -0.132102 |      21 |             8 |      29 | 2022-01-28 16:18:00 |    0.724138  |
```

Yo he puesto estas dos funciones en un archivo llamado *[download.py](http://download.py)* en la raíz de mi repositorio; más adelante lo usaré.

# Graficando la información

Hay cerca de 750 estaciones de bicicleta en Londres, como quiero hacer esta información lo más accesible posible se me ocurrió que la mejor forma de hacerlo era a través de una imágen mostrando la ocupación de cada una de estas estaciones. 

## Consiguiendo un mapa

Antes de comenzar, necesito un mapa de Londres en un formato que la computadora pueda interpretar, y justamente encontré uno que inclusive puedo descargar programáticamente en el sitio web del gobierno de la ciudad. Para hacerme la vida más fácil, me cree un archivo *Makefile* con una tarea llamada `shapefiles` que descarga y mueve los archivos necesarios:

```makefile
shapefiles:
	wget https://data.london.gov.uk/download/statistical-gis-boundary-files-london/9ba8c833-6370-4b11-abdc-314aa020d5e0/statistical-gis-boundaries-london.zip
	unzip statistical-gis-boundaries-london.zip
	mv statistical-gis-boundaries-london/ESRI shapefiles/
	rm -rf statistical-gis-boundaries-london statistical-gis-boundaries-london.zip
```

Lo que nos debería dejar con un folder llamado *shapefiles* cuyo contenido es el siguiente:

```makefile
shapefiles
├── London_Borough_Excluding_MHW.GSS_CODE.atx
├── London_Borough_Excluding_MHW.NAME.atx
├── London_Borough_Excluding_MHW.dbf
├── London_Borough_Excluding_MHW.prj
├── London_Borough_Excluding_MHW.sbn
├── London_Borough_Excluding_MHW.sbx
├── London_Borough_Excluding_MHW.shp
├── London_Borough_Excluding_MHW.shp.xml
└── London_Borough_Excluding_MHW.shx
```

## Graficando un mapa

La cosa es más o menos sencilla, estoy planeando otro post en Tacos de Datos en donde podemos entrar en profundidad sobre cómo podemos graficar esta información de mejor manera, así que solamente les voy a poner el código y hablar en términos generales de lo que sucede.

```python
def plot_map(cycles_info: pd.DataFrame) -> str:
    london_map = gpd.read_file("shapefiles/London_Borough_Excluding_MHW.shp").to_crs(epsg=4326)

    fig = plt.figure(figsize=(6, 4), dpi=170)
    ax = fig.gca()

    london_map.plot(ax=ax)
    sns.scatter(y="lat", x="lon", hue="proportion", palette="Blues", data=cycles_info, s=25, ax=ax)

    prepare_axes(ax, cycles_info)

    map_file = save_fig(fig)

    return map_file
```

Lo primero es leer el archivo *.shp* del mapa que vamos a usar. Después creamos una figura y tomamos el *axes* para dibujar en él. Dibujamos el mapa usando el método `plot` del `GeoDataFrame`. Usamos *seaborn* para poner las estaciones en el mapa, toma en cuenta que estamos especificando la ubicación (lat, lon) para cada punto, la coloración de cada punto estará definida por la columna `proportion` y por último el tamaño de cada uno de ellos será `25`. Para terminar realizamos algunos ajustes al eje y guardamos la figura en una dirección temporal solamente para regresar la ruta en donde la imagen generada está guardada.

(Puedes ver el resto del código acá, o espera a que publique la explicación en Tacos de Datos)

El resultado es el siguiente:

Guardé esta función en un archivo separado llamado *plot.py*.

# Tuiteando la información

Ya tenemos la imagen, es hora de tuitearlo usando *Twython*, vamos a necesitar unos cuantos secretos que obtendremos de Twitter en el post siguiente, por el momento, vamos a pretender que ya los tenemos. Vamos a usar esos secretos para crear un cliente de `Twython`:

```python
app_key = os.environ["API_KEY"]
app_secret = os.environ["API_SECRET"]
oauth_token = os.environ["ACCESS_TOKEN"]
oauth_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)
```

La forma en la que la API de Twitter funciona requiere que nosotros carguemos primero la imagen a su servicio y después la tuiteemos, para ambas cosas vamos a usar la variable `twitter` recien creada, el truco es usar el `media_id` que recuperamos de cargar la imagen:

```python
with open(image_path, "rb") as cycles_png:
    image = twitter.upload_media(media=cycles_png)

now = datetime.now().strftime("%m/%d/%Y, %H:%M")
twitter.update_status(
    status=f'London Cycles update at {now}',
    media_ids=[image['media_id']]
)
```

Solo para modularizar el código puse este código dentro de una función y esta función en su propio archivo *tweeter.py*.

# Conclusión

Ya tenemos todo en su lugar, ahora podemos combinar todas nuestras funciones para lograr que con un solo script descarguemos información, generemos un mapa y lo tuiteemos:

```python
from download import download_cycles_info
from plot import plot_map
from tweeter import tweet

def execute():
    information = download_cycles_info()
    map_image = plot_map(information)
    tweet(map_image)
```

Guardé este código en un archivo llamado *app.py*. Así es como [se ve el repositorio](https://github.com/fferegrino/tweeting-cycles-lambda/tree/part-1-python) al terminar este post.

Recuerda que me puedes encontrar en Twitter [en @io_exception](https://twitter.com/io_exception) para preguntarme sobre este post, el código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon) 
