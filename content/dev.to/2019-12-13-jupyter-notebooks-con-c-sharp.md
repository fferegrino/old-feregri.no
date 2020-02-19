---
layout: post
language: es
original_url: https://dev.to/fferegrino/jupyter-notebooks-con-c-2epp
title:  Jupyter Notebooks con C# 
date: 2019-12-13 14:00:00
tags: csharp, jupyternotebooks, data-science
short_summary: Los Jupyter Notebooks llegaron a C#, aquí te enseño cómo instalarlos.
---  

No hay duda que los Jupyter Notebooks se han establecido como una herramienta esencial cuando de hacer análisis de datos se trata, sin embargo, estos son comúnmente asociados con Python, pero esto ya no es así. Recientemente, y gracias a la gente de [Try .NET](https://github.com/dotnet/try) ahora es posible disfrutar de C# en los famosos Notebooks.


#### Sobre Jupyter  
Hice un [video sobre Jupyter](https://www.youtube.com/watch?v=xcXky3PxVHA), pero en corto: para funcionar, cada Notebook en Jupyter está asociado con un entorno de ejecución (*runtime*), que es creado a partir de un **kernel**, es dentro de este *runtime* que se ejecutan todos los bloques de código que creamos. Por default, Jupyter viene con el **kernel de Python**

### Instalando (Windows)

Si usas Linux, [checa este Dockerfile](https://github.com/fferegrino/scisharp/blob/master/Dockerfile) para ver los pasos para instalar todo.

Primero que nada, asegúrate de tener [.NET Core](https://dotnet.microsoft.com/download/dotnet-core) instalado, la cualquier versión arriba de 2.1 será suficiente.

Luego toca instalar Jupyter Lab, si no tienes Python te invito a que le eches un ojo a [este post](https://dev.to/fferegrino/my-basic-windows-setup-4gdh) en el que te cuento cómo preparar Python en Windows. Si seguiste la guía, será suficiente con ejecutar `pipenv install jupyterlab` para instalarlo en un entorno, o también puedes instalarlo a nivel de sistema usando `pip install jupyterlab`. 

En la introducción hablé de los **kernels**, y para instalar el **kernel de C#** debes ejecutar los siguientes comandos en una consola: 

Para instalar la herramienta `dotnet-try`:

```
dotnet tool install --global dotnet-try
```

Para instalar el kernel de .NET:

```
dotnet try jupyter install
```

Y por último, para confirmar que todo salió bien, ejecuta

```
jupyter kernelspec list
```

Deberás ver algo como esto:

```
Available kernels:
.net-sharp    ...
.net-fsharp   ...
python3       ...
```

Y si es así, ya tienes todo para empezar a usar los C# notebooks.

### Breve introducción  

Para comenzar basta con ejecutar el comando `jupyter lab` y se deberá abrir una ventana del navegador. Verás que del lado derecho te sale una opción para crear un nuevo notebook usando C#, basta con darle click para que se abra una pantalla como esta:


![A blank C# Notebooks](https://thepracticaldev.s3.amazonaws.com/i/haqkknp75dnfu5y6t990.png)

De nueva cuenta, te recomiendo que le eches un ojo a mi [video sobre Jupyter](https://www.youtube.com/watch?v=xcXky3PxVHA) si no sabes nada sobre los Notebooks.  

 - **Imprimir cosas en pantalla**: Puedes usar el famoso método:


```csharp
Console.WriteLine("Hola mundo!");
```

Aunque para imprimir también podemos usar el método:

```csharp
display("Hola mundo");
```

Además de que usar el método `display` nos pemritirá personalizar la forma en que se muestran los datos si usamos los [object formatters](https://github.com/dotnet/try/blob/master/NotebookExamples/csharp/Docs/Object%20formatters.ipynb)

 - **Instalar NuGet packages**: se usa la [directiva de pre-procesamiento](https://thatcsharpguy.com/posts/directivas-de-preprocesamiento-en-c/) `#r`:  

```csharp
// #r "nuget:<package name>,<package version>"
#r "nuget:MathNet.Numerics, 4.9.0"
```

 - **Usar otros namespaces**: No hay que hacer nada en especial, lo mismo de siempre:

```csharp
using MathNet.Numerics;
using KernelDensity = MathNet.Numerics.Statistics.KernelDensity;
``` 

Eso es todo por el momento, en el siguiente post les hablaré de algunos paquetes para hacer análisis de datos y graficar con C#, todo dentro de un C# Notebook! por el momento, si tienen alguna duda, me pueden contactar vía Twitter en [@io_exception](https://twitter.com/io_exception).

Por cierto: Esta publicación es parte del Segundo Calendario de Adviento de C# en Español, una iniciativa liderada por [Benjamín Camacho](https://twitter.com/jbenjamincc). Revisa [este enlace](https://aspnetcoremaster.com/calendario-adviento-csharp-2019.html) para conocer más artículos interesantes sobre C# publicados por varios miembros de la comunidad. 
