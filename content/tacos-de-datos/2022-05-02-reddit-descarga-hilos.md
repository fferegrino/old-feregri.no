---
layout: post
language: es
title: Graficando datos de Reddit
date: 2022-05-02 10:00:00
short_summary: Vamos a descargar una cantidad enorme de datos de Reddit para investigar el interés de los usuarios sobre un tema
original_url: https://www.tacosdedatos.com/ioexception/word2vec-ilustrado-5blj
---  

## Leyendo los *threads*

Los archivos se dividen en dos grupos principales:

 - El archivo *threads.csv* y,
 - Los archivos *comments/comments_[THREAD_ID].csv*

El primer grupo es un único archivo que contiene información de alto nivel que actúa como agregador para el resto de los archivos. En este archivo se puede encontrar el nombre, el autor, el título, la fecha de creación, la puntuación y el número de comentarios de cada uno de los *live threads* relacionados con la invasión.

```python file="threads.jpg" tags=[]
threads = pd.read_csv("data/threads.csv")
threads.head(2)
```

![Archivo threads.csv](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/threads.jpg?ik-sdk-version=javascript-1.4.3&updatedAt=1651473454007)

El segundo grupo contiene tantos archivos como hilos existan en el archivo *threads.csv*; cada uno tiene un nombre como *comments/comments_[THREAD_ID].csv*.

Cada fila de estos archivos *csv* representa un comentario realizado en el hilo padre. La información disponible para cada comentario es: autor, identificador, cuerpo, fecha/hora de creación, si ha sido editado, puntuación y el comentario padre (si es una respuesta).

Una cosa que hay que tener en cuenta es que no se puede utilizar simplemente `pd.read_csv`, ya que a veces los comentarios pueden contener saltos de línea que hacen que a veces un solo comentario utilice más de una fila en el archivo. Para leer correctamente todos estos archivos, hay que pasar el argumento `lineterminator`:

```python file="sample-comments.jpg" tags=[]
file = "data/comments/comments__st8lq0.csv"
comments = pd.read_csv(file, lineterminator="\n")
comments.head(2)
```

![Ejemplo de comentarios](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/sample-comments.jpg?ik-sdk-version=javascript-1.4.3&updatedAt=1651473454007)

## Graficando la frecuencia de los comentarios

Ahora que hemos aprendido lo que contienen los archivos y cómo leerlos, vamos a hacer algo interesante con ellos. Veamos cómo ha cambiado el interés en el hilo a lo largo del tiempo contando el número de comentarios por hora.

En general, el proceso es el siguiente:

 1. Leer todas las fechas de los comentarios
 2. Agrupar las fechas en intervalos de 1 hora
 3. Graficar

### 1. Leer todas las fechas de los comentarios

Podemos seguir usando *pandas* pero siendo más inteligentes en su uso. ¿Sabías que puedes especificar que sólo quieres un subconjunto de columnas con el argumento `usecols`?

```python
created_dates = []
for thread_id in threads["id"]:
    comments_file = f"data/comments/comments__{thread_id}.csv"
    data = pd.read_csv(comments_file, lineterminator="\n", usecols=["created_utc"])
    created_dates.append(data["created_utc"].values)

created_dates = np.concatenate(created_dates)
```

Esto nos deja con el *NumPy array* `created_dates` que contiene $2,083,085$ números que representan la fecha de creación de cada comentario. El siguiente paso es agrupar estas fechas en intervalos de 1 hora.

### 2. Agrupando los tiempos de creación

Utilizaremos un par de funciones de ayuda para redondear las horas de las fechas hacia arriba o hacia abajo al paso más cercano en el intervalo que definamos (y una más para visualizar las marcas de tiempo).

```python
# Helper date functions
INTERVAL = 3600  # 1 hour in seconds


def lower_bound(ts):
    return ts - (ts % INTERVAL)


def upper_bound(ts):
    return ts + (INTERVAL - ((ts) % INTERVAL) if (ts) % INTERVAL != 0 else 0)


def humanise(ts):
    return datetime.fromtimestamp(ts).strftime("%m/%d/%Y, %H:%M:%S")
```

Por ejemplo, toma la fecha *04/29/2022, 20:20:58* cuyo timestamp es `1651263658`:

```python
example_ts = 1651263658
actual_date = humanise(1651263658)
upper = humanise(upper_bound(example_ts))
lower = humanise(lower_bound(example_ts))

print(f"{lower} is the lower bound of {actual_date} and its upper bound is {upper}")
```

Ahora que tenemos una forma de calcular los límites superior e inferior de una fecha concreta, podemos pasar a calcular los bordes de los contenedores. Esto es fácil una vez que conocemos las fechas mínimas y máximas en nuestro arreglo `created_dates`. De hecho, obtener los bordes del contenedor es una simple línea con *NumPy*:

```python
bin_edges = np.arange(
    start=lower_bound(min(created_dates)),
    stop=upper_bound(max(created_dates)) + 1,
    step=INTERVAL,
    dtype=int,
)
```

¿He dicho una sola línea? 😅 - bueno, quería que fuera más comprensible. La parte inteligente viene cuando añadimos 1 al límite superior; ya que `np.arange` es exclusivo en el lado derecho, lo que significa que nuestro límite superior válido no sería devuelto, sin embargo, eludimos esta limitación haciendo que parezca que nuestro límite superior no es el último número. Por último, el argumento `step` tiene que ser igual a 1 hora.

Ahora que tenemos los bordes de los contenedores, estamos listos para calcular el histograma. Esta es otra función de una sola línea, ¡gracias a `np.histogram` de NumPy!

```python
values, bin_edges = np.histogram(created_dates, bins=bin_edges)
```

Los valores devueltos por esta función son el recuento para el intervalo especificado y los propios intervalos. ¡Ten en cuenta que siempre habrá un elemento más en los intervalos que en los valores!

#### ¿Una ventana?

Para una mayor personalización podemos especificar una determinada ventana de tiempo que queramos mostrar por si queremos "hacerle zoom" nuestro gráfico. Por ahora, dado que los hilos en vivo comenzaron el 14 de febrero de 2022, tomaremos eso como el comienzo de nuestra ventana y en cuanto al final, tomaremos la fecha máxima disponible + 1 día.

```python
begining = datetime(2022, 2, 14)
end = datetime.fromtimestamp(bin_edges[-1]).replace(hour=0, minute=0) + timedelta(days=1)
window = (begining, end)
```

#### Convirtiendo en un *pandas Series*

Para facilitarnos la tarea, vamos a convertir nuestros valores y cubetas en una *Serie* de *pandas*:

```python
comments_histogram = pd.Series(data=values, index=pd.to_datetime(bin_edges[:-1], unit="s"))
```

#### Eventos importantes

El gráfico es informativo; sin embargo, podemos hacerlo aún más útil con algunos eventos importantes sobre la invasión - esto ayudará a nuestros usuarios a evaluar cómo un evento particular en la vida real se traduce en un pico (o no) en los comentarios en línea.

Necesitamos crear un array de tuplas, donde cada tupla es la fecha de cuando ocurrió el evento y una breve descripción del mismo:

```python
major_events = [
    (datetime(2022, 2, 21, 19, 35), "Russia recognizes the\nindependence of\nbreakaway regions"),
    (datetime(2022, 2, 24, 3, 0), 'Putin announces the\n"special military operation"\nin Ukraine'),
    (datetime(2022, 3, 16, 16, 0), "Chernihiv breadline massacre\n and Mariupol theatre airstrike"),
    (datetime(2022, 4, 3, 17, 42), "Discovery of the\nBucha massacre"),
    (datetime(2022, 4, 13, 17, 42, 42), "Sinking of the Moskva"),
    (datetime(2022, 4, 28, 6, 49), "US Government approves\nLend-lease for Ukraine"),
]
```

## 3. ¡Graficar!

Por fin, la parte que todos esperaban. Empecemos por configurar algunas opciones de *matplotlib*:

```python
params = {
    "axes.titlesize": 20,
    "axes.labelsize": 15,
    "lines.linewidth": 1.5,
    "lines.markersize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 12,
}

mpl.rcParams.update(params)
```

#### Una gráfica basica

Vamos a probar un plot básico inicial - creado con una función para que podamos reutilizarlo después

```python description="First version" file="first-version.png" tags=[]
def line_plot():
    fig = plt.figure(figsize=(25, 7), dpi=120)
    ax = fig.gca()
    ax.plot(comments_histogram.index, comments_histogram, color="#005BBB")
    ax.fill_between(comments_histogram.index, comments_histogram, color="#cce5ff", alpha=0.5)
    return fig, ax


line_plot()
```

![First version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/first-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651354449381)

No está mal, pero se puede mejorar más.

#### Mejorando los marcadores con *locators* and *formatters*

Lo primero que me gustaría abordar es el hecho de que las referencias visuales en términos de días y recuento de comentarios parecen muy escasas. Dado que se trata de observaciones diarias, me parece que puede ser útil mostrar esta información en el gráfico.

Resulta que *matplotlib* tiene algunas utilidades estupendas que podemos emplear al trabajar con fechas dentro del paquete `matplotlib.dates`.

La función `add_ticks` se divide en 4 bloques:

 1. Establecer los ticks menores en el eje X, utilizando `DayLocator` y `DateFormatter` para establecer un marcador menor cada día
 2. Establecer las marcas mayores en el eje X, utilizando un `MonthLocator` y un `DateForamtter` para establecer un marcador mayor cada mes
 3. Establecer el formato en el eje Y; esto es un poco más complicado ya que necesitamos establecer "manualmente" los ticks leyendo los originales con `FixedLocator`, y luego usar un `FuncFormatter` (y una función lambda) para especificar el nuevo formato.
 4. Establece algunos estilos adicionales para que los ticks mayores destaquen sobre los menores.

```python description="Second version" file="second-version.png" tags=[]
def add_ticks(axes):

    minor_locator = mdates.DayLocator(interval=1)
    minor_formatter = mdates.DateFormatter("%d")
    axes.xaxis.set_minor_locator(minor_locator)
    axes.xaxis.set_minor_formatter(minor_formatter)

    major_locator = mdates.MonthLocator(interval=1)
    major_formatter = mdates.DateFormatter("%b")
    axes.xaxis.set_major_locator(major_locator)
    axes.xaxis.set_major_formatter(major_formatter)

    ticks_loc = axes.get_yticks()
    axes.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    axes.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, pos: f"{int(val / 1000)}K"))

    ax.tick_params(axis="x", which="major", length=20)
    ax.tick_params(which="major", labelsize=15)


fig, ax = line_plot()
add_ticks(ax)
```

![Second version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/second-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981035)

Si me preguntas, creo que se ve mejor.

#### ¿Dónde están mis etiquetas?

Un gráfico sin etiquetas es un gráfico pobre; guiados por este principio, vamos a añadir la función `add_legends` dividida en dos bloques:

 - Establece los límites de lo que muestra el gráfico; aquí es donde utilizamos la `window` definida anteriormente y establecemos el punto de partida del eje Y en 0.
 - Establece todas las etiquetas y el crédito del gráfico.

```python description="Third version" file="third-version.png" tags=[]
def add_legends(axes, window):

    axes.set_ylim(ymin=0)
    axes.set_xlim(window)

    axes.set_title("r/WorldNews interest over the Russian Invasion of Ukraine")
    axes.set_xlabel("Day")
    axes.set_ylabel("Hourly comments")
    credit = f"u/fferegrino - comments from r/worldnews live threads"
    axes.add_artist(AnchoredText(credit, loc=1, frameon=True))


fig, ax = line_plot()
add_ticks(ax)
add_legends(ax, window)
```

![Third version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/third-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981190)

Ahora la gente sabe de qué se trata el gráfico. Todavía no estamos ahí, pero nos estamos acercando.

#### Eventos importantes

¿Recuerdas que creamos un array de tuplas llamado `major_events`? Ahora es su momento de brillar. La función `add_highlighted_events` toma el eje y la matriz de eventos principales e itera sobre ellos, marcando sus ubicaciones con el método `.annotate.`:

```python description="Fourth version" file="fourth-version.png" tags=[]
def add_highlighted_events(axes, events):
    for date, title in events:
        event_utc_date = datetime.fromtimestamp(lower_bound(date.astimezone(pytz.utc).timestamp()))
        arrow_tip_location = comments_histogram[event_utc_date]
        xy = (event_utc_date, arrow_tip_location)
        xy_text = (event_utc_date - timedelta(days=0.6), arrow_tip_location + 4_000)
        arrow_props = dict(arrowstyle="-|>", facecolor="black")

        axes.annotate(
            title,
            xy=xy,
            xytext=xy_text,
            ha="right",
            arrowprops=arrow_props,
            fontsize=15,
        )


fig, ax = line_plot()
add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)
```

![Fourth version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/fourth-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981161)

#### Más color

En la función `add_final_touches`, encontrarás que estoy añadiendo una cuadrícula para que haya una sutil distinción entre los días. Ponemos el color de fondo de la trama en amarillo claro y el fondo general de nuestro gráfico en blanco. 

```python description="Fifth version" file="fifth-version.png" tags=[]
def add_final_touches(figure, axes):

    axes.grid(axis="x", which="both", color="#FFEE99")
    axes.set_facecolor("#FFF7CC")
    figure.patch.set_facecolor("white")
    figure.tight_layout()


fig, ax = line_plot()
add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)
add_final_touches(fig, ax)
```

![Fifth version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/fifth-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981153)

Y ya podemos comenzar a guardar la imagen:

```python
fig.savefig("worldnews.png")
```

#### Apéndice: Datos que faltan el 26 de febrero

¿Ves el descenso entre el 26 y el 27 de febrero? veamos qué ha pasado:

El último comentario en el hilo del [Day 3, Part 6 (Thread #35)](https://reddit.com/r/worldnews/comments/t1oqrc/rworldnews_live_thread_russian_invasion_of/) se publicó a las 06:54:34 AM, mientras que el comentario más temprano en el hilo de reemplazo, [Day 3, Part 7 (Thread #36)](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/?sort=old) es de las 07:57:52 AM.

Esto hace pensar que no hubo absolutamente ningún comentario durante una hora. Sin embargo, al investigar más a fondo, parece que hubo un error en el equipo de mods donde uno de ellos creó un hilo con el nombre equivocado, lo dejó alrededor de 1 hora y luego lo borró, como lo demuestran estos comentarios:

 > What happened to the last thread? – [*permalink*](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/hyhpo2p/)
 >> Had the dates wrong, said it was day 4 thread 1.

Y

 > New thread already? – [*permalink*](https://www.reddit.com/r/worldnews/comments/t1rnuj/rworldnews_live_thread_russian_invasion_of/hyhpn5g/?utm_source=reddit&utm_medium=web2x&context=3)
 >> Wrong day on the last one

Añadamos otra nota a nuestra grafica para que la gente no se confunda:

```python description="Sixth version" file="sixth-version.png" tags=[]
fig, ax = line_plot()

add_ticks(ax)
add_legends(ax, window)
add_highlighted_events(ax, major_events)
add_final_touches(fig, ax)

ax.annotate(
    "Mod-deleted post",
    xy=(datetime(2022, 2, 26, 6, 45), 0),
    xytext=(datetime(2022, 2, 26, 6, 45) + timedelta(hours=24), 500),
    ha="left",
    arrowprops=dict(arrowstyle="-|>", facecolor="black", alpha=0.5),
    fontsize=15,
    alpha=0.5,
)

fig.savefig("worldnews.png")
```

![Sixth and final version](https://ik.imagekit.io/thatcsharpguy/posts/worldnews/sixth-version.png?ik-sdk-version=javascript-1.4.3&updatedAt=1651353981204)

## Conclusion

Y ya está, tenemos un gráfico aún más interesante de ver (y también fue divertido hacerlo).

En un post anterior, vimos cómo crear un conjunto de datos utilizando los datos de Reddit, y en este vimos cómo utilizar este conjunto de datos para crear algo que se pueda presentar. Espero que hayas aprendido algo nuevo o al menos que te haya gustado. Como siempre, [el código está disponible aquí](https://github.com/fferegrino/r-worldnews-live-threads-ukraine/blob/main/plot.ipynb), y estoy abierto a responder cualquier pregunta en [Twitter en @io_exception](https://twitter.com/io_exception).
