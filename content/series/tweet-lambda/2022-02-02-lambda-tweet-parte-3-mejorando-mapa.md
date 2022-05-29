---
layout: post
language: es
title: Mapas con GeoPandas – Bot con AWS Lambda: P3
date: 2022-02-02 10:00:03
short_summary: Vamos a mejorar un poco la apariencia del mapa usando algunas configuraciones específicas de GeoPandas y Seaborn
tags: python, github, aws, geopandas, seaborn
social_image: https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/cycles-part-3_Pox7NGAWx.jpg
slug: lambda-tweet-parte-3-mapas-geopandas
--- 

Esta serie de posts consta de 8 entregas, siendo esta la tercera en donde vamos a mejorar un poco la apariencia del mapa usando algunas configuraciones específicas de GeoPandas y Seaborn. Los otros posts en la serie abordan a su vez un aspecto muy específico del problema, puedes encontrarlos aquí:

 - Configurando Twitter y AWS - [Parte 1](/lambda-tweet-parte-1-github-aws-twitter)
 - Programando la lambda con Python - [Parte 2](/lambda-tweet-parte-2-python)
 - Mejorando el mapa con GeoPandas - [Parte 3](/lambda-tweet-parte-3-mapas-geopandas)
 - Creando la lambda en un contenedor - [Parte 4](/lambda-tweet-parte-4-contenedor-lambda)
 - Infraestructura con Terraform - [Parte 5](/lambda-tweet-parte-5-terraform)
 - Automatización con GitHub Actions - [Parte 6](/lambda-tweet-parte-6-github-actions)
 - Agregando pruebas con Pytest - [Parte 7](/lambda-tweet-parte-7-add-testing)
 - Optimizando Docker - [Parte 8](/lambda-tweet-parte-8-aligerando-docker)
 
---

Para este post vamos a estar trabajando con información relacionada con las estaciones de bicicletas, esta información fue descargada de la API de TFL (la red de transporte público de Londres), la información es la siguiente:

| id             | name                 |     lat |       lon |   bikes |   empty_docks |   docks | query_time          |   proportion |
|:---------------|:---------------------|--------:|----------:|--------:|--------------:|--------:|:--------------------|-------------:|
| BikePoints_489 | Christian Street,... | 51.5131 | -0.064094 |       8 |            26 |      34 | 2022-01-30 07:39:00 |     0.235294 |
| BikePoints_591 | Westfield Library... | 51.5061 | -0.224223 |      26 |             0 |      27 | 2022-01-30 07:39:00 |     1        |
| BikePoints_437 | Vauxhall Walk, Va... | 51.4881 | -0.120903 |      22 |             3 |      27 | 2022-01-30 07:39:00 |     0.888889 |
| BikePoints_165 | Orsett Terrace, B... | 51.5179 | -0.183716 |      13 |             2 |      15 | 2022-01-30 07:39:00 |     0.866667 |
| BikePoints_317 | Dickens Square, B... | 51.4968 | -0.093913 |      32 |             0 |      32 | 2022-01-30 07:39:00 |     1        |

De este dataframe, que en el código voy a nombrar `cycles_info`, lo que a mi me interesa es únicamente las columnas: `lat` y `lon`, que es la ubicación de cada una de las estaciones y la columna `proportion` que tiene un rango `[0, 1]`, en donde `0` indica que la estación no tiene bicicletas disponibles y `1` que significa que la estación está llena.

Además de que para tener una referencia geográfica de la ubicación de cada uno de estos puntos voy a usar un mapa (en formato vectorial [llamado Shapefile](https://es.wikipedia.org/wiki/Shapefile)) de la ciudad de Londres; este archivo lo encontré en la [página web de London Datastore](https://data.london.gov.uk/dataset/statistical-gis-boundary-files-london).

Hablando un poco sobre el formato de este post, en esta ocasión iré transformando de a poco la gráfica hasta llegar al resultado final, que se ve más o menos así:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/06_-_map-with-stations-centered_VYKfJed9Igv.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/06_-_map-with-stations-centered_VYKfJed9Igv.png)

Si llevas mucha prisa y quieres ver el código final, puedes ir directamente al final del post. Si quieres saber cómo llegué a ese código, sigue leyendo.

# La API orientada a objetos

A mi siempre me ha gustado usar en la medida de lo posible la API orientada a objetos de *matplotlib*, además de estar familiarizado con este paradigma de programación, usar esta API permite personalizar las gráficas al máximo.

Para nuestros propósitos vamos a comenzar creando una instancia de `Figure` y una de `Axes`:

```python
fig = plt.Figure(figsize=(6, 4), dpi=200, frameon=False)
ax = plt.Axes(fig, [0., 0., 1., 1.])
fig.add_axes(ax)
```

Esto creará una gráfica vacía:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/00_-_empty-axe_HIdM1dPOK.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/00_-_empty-axe_HIdM1dPOK.png)

# *Geopandas* y *shapefiles*

Ahora vamos a abrir nuestro archivo *.shp* y a graficarlo en el `ax` que acabamos de crear:

```python
london_map = gpd.read_file("shapefiles/London_Borough_Excluding_MHW.shp").to_crs(epsg=4326)
london_map.plot(ax=ax)
```

El método `to_crs` nos ayuda a re-proyectar la información geoespacial a otro sistema de coordenadas de referencia (*Cordinate Reference System*), con `epsg=4326` la proyección es la que nosotros coloquialmente conocemos como latitud y longitud.

El resultado de graficar de esa manera es el siguiente:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/01_-_map-as-is_sM-Xhy_mS.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/01_-_map-as-is_sM-Xhy_mS.png)

Londres comienza a tomar forma.

# Colocando las estaciones

Ya que tenemos nuestro mapa, el siguiente paso es colocar las estaciones de bicicleta, para esto usaré la biblioteca *seaborn*, y una *scatter plot*:

```python
sns.scatterplot(y="lat", x="lon", hue="proportion", data=cycles_info, ax=ax)
```

Al método `scatterplot` le especificamos qué columna del *data frame* usar para los ejes *x* e *y*, también le estamos diciendo de dónde tomar el color para cada uno de los puntos, esto lo hacemos a través del argumento `hue`, recuerda que la columna `proportion` va de *0* a *1*. Para finalizar le decimos de qué data frame debe sacar la información y en qué *axes* debe graficar:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/02_-_map-with-stations_c09TxIUGanb.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/02_-_map-with-stations_c09TxIUGanb.png)

Sí, aún deja mucho que desear, vamos paso a paso.

# Haciéndole zoom

¿Te das cuenta de la desigualdad en Londres?: las bicicletas solo cubren la zona central de la ciudad... pero bueno, ese es otro tema.

Para asegurarnos de que nuestra información es un poco más fácil de consumir vamos a centrar la gráfica en la zona en la que se concentra toda la información, usaremos los métodos `set_ylim` y `set_xlim` (ya que estamos en eso, vamos a quitarle los ejes que están de más en nuestra gráfica):

```python
ax.set_ylim((min_y, max_y))
ax.set_xlim((min_x, max_x))
ax.set_axis_off()
```

Los valores de `min_y` y `min_x` corresponden con la latitud mínima y máxima, y `min_x` y `max_x` corresponden con los mismos valores, pero en este caso de la longitud. El resultado es este:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/03_-_map-with-stations-centered_ZAxaM15RL.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/03_-_map-with-stations-centered_ZAxaM15RL.png)

Nos vamos acercando a un resultado más o menos aceptable.

# Coloreando el mapa

Los colores del mapa no son tan agradables, hasta pareciera que lo que es suelo es agua y que el río Támesis está vacío. Para colorear el río de color azul usaré el método `fill_between` y las coordenadas obtenidas previamente. Para el mapa tenemos que cambiar lso argumentos de `plot` en nuestro *geodata frame*:

```python
ax.fill_between([min_x, min_y], min_y, max_y, color="#9CC0F9")
london_map.plot(ax=ax, linewidth=0.5, color='#F4F6F7', edgecolor='black')
```

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/04_-_map-with-stations-centered_1umeXPQpe.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/04_-_map-with-stations-centered_1umeXPQpe.png)

# Cambiando el color de las estaciones

Ahora que cambiamos el color del mapa, siento que el color de las estaciones se pierde un poco, ¿no? – vamos a cambiar esos colores morados por unos tonos rojos. Para esto usaremos una paleta de colores (o *color map*) de *matplotlib* conocida como *OrRd*, esta paleta se convertirá en un argumento para el método *scatterplot* de *seaborn*:

```python
cmap = matplotlib.cm.get_cmap("OrRd")
sns.scatterplot(
		y="lat", x="lon", hue="proportion", edgecolor="k", linewidth=0.1, palette=cmap, data=cycles_info, s=20, ax=ax
)
```

El único cambio que sufrió la llamada a *scatterplot* es en el argumento `palette`, al final el resultado es:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/05_-_map-with-stations-centered_JuHmHRq1Gf.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/05_-_map-with-stations-centered_JuHmHRq1Gf.png)

Ugh, aún nos queda esa leyenda tan grande e invasiva...

# Leyenda personalizada

En lugar de la leyenda por default, quiero poner algo más “sofisticado”, más legible a simple vista. Si recuerdas, los valores van de *0* a *1*, entre más claro el color es, más cercano a *0*. Imagina una escala así:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/palette-3x_ivAiWnef8lH.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/palette-3x_ivAiWnef8lH.png)

Esos tres niveles son justamente los que quiero mostrar. Para obtener los valores de los colores correctos vamos a crear un arreglo de (valor, etiqueta); después podemos usar nuestro `cmap` creado en el paso anterior para obtener el color adecuado. Por último, creamos tantas instancias de `Line2D` como elementos queramos dentro de la leyenda.

```python
values = [(0.0, "Empty"), (0.5, "Busy"), (1.0, "Full")]
legend_elements = []
for gradient, label in values:
		color = cmap(gradient)
    legend_elements.append(
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=label,
            markerfacecolor=color,
            markeredgewidth=0.5,
            markeredgecolor="k",
        )
    )

ax.legend(handles=legend_elements, loc="lower right", prop={"size": 6}, ncol=len(values))
```

La línea final reemplaza nuestra etiqueta anticuada por la que acabamos de ensamblar; con `loc` se le especifica que queremos que aparezca abajo a la derecha, con `prop={"size": 6}` indicamos el tamaño de las etiquetas y `ncol` le dice a *matplotlib* que la leyenda se compone de 3 columnas, esto lo hago con la finalidad de que la leyenda presente sus valores de forma horizontal:

![https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/06_-_map-with-stations-centered_VYKfJed9Igv.png](https://ik.imagekit.io/thatcsharpguy/posts/python-lambdas/06_-_map-with-stations-centered_VYKfJed9Igv.png)

# Código final

```python
from typing import Tuple

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import Colormap
from matplotlib.lines import Line2D

PADDING = 0.005

def prepare_axes(ax: plt.Axes, cycles_info: pd.DataFrame) -> Tuple[float, float, float, float]:
    min_y = cycles_info["lat"].min() - PADDING
    max_y = cycles_info["lat"].max() + PADDING
    min_x = cycles_info["lon"].min() - PADDING
    max_x = cycles_info["lon"].max() + PADDING
    ax.set_ylim((min_y, max_y))
    ax.set_xlim((min_x, max_x))
    ax.set_axis_off()
    return min_x, max_x, min_y, max_y

def save_fig(fig: plt.Figure) -> str:
    fig.patch.set_facecolor("white")
    map_file = "/tmp/map.png"
    fig.savefig(map_file)
    return map_file

def set_custom_legend(ax: plt.Axes, cmap: Colormap) -> None:
    values = [(0.0, "Empty"), (0.5, "Busy"), (1.0, "Full")]
    legend_elements = []
    for gradient, label in values:
        color = cmap(gradient)
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=label,
                markerfacecolor=color,
                markeredgewidth=0.5,
                markeredgecolor="k",
            )
        )
    ax.legend(handles=legend_elements, loc="lower right", prop={"size": 6}, ncol=len(values))

def plot_map(cycles_info: pd.DataFrame) -> str:
    fig = plt.Figure(figsize=(6, 4), dpi=200, frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    fig.add_axes(ax)

    # Calculate & set map boundaries
    min_x, max_x, min_y, max_y = prepare_axes(ax, cycles_info)

    # Get external resources
    cmap = plt.get_cmap("OrRd")
    london_map = gpd.read_file("shapefiles/London_Borough_Excluding_MHW.shp").to_crs(epsg=4326)

    # Plot elements
    ax.fill_between([min_x, max_x], min_y, max_y, color="#9CC0F9")
    london_map.plot(ax=ax, linewidth=0.5, color="#F4F6F7", edgecolor="black")
    sns.scatterplot(
        y="lat", x="lon", hue="proportion", edgecolor="k", linewidth=0.1, palette=cmap, data=cycles_info, s=25, ax=ax
    )

    set_custom_legend(ax, cmap)

    map_file = save_fig(fig)

    return map_file
```

Listo, ¡eso es todo!

Así es como [se ve el repositorio](https://github.com/fferegrino/tweeting-cycles-lambda/tree/part-2-map-improvements) al terminar este post.

Recuerda que me puedes encontrar en Twitter [en @feregri_no](https://twitter.com/feregri_no) para preguntarme sobre este post – si es que algo no queda tan claro o encontraste un *typo*. El código final de esta serie [está en GitHub](https://github.com/fferegrino/tweeting-cycles-lambda) y la cuenta que tuitea el estado de la red de bicicletas es [@CyclesLondon](https://twitter.com/CyclesLondon) 
