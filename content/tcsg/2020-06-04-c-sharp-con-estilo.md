---
layout: post
lannguage: es
title: C# con estilo (a la fuerza)
original_url: https://thatcsharpguy.com/post/c-con-estilo-a-fuerzas
date: 2020-06-04 12:00:00
author: Antonio Feregrino
short_summary: ¿A quién no le gusta el código escrito siguiendo un estandar? te muestro como puedes aplicar el tuyo en .NET
lang: es
tags: c-sharp, Windows
---

¿Has escuchado de las guías de estilo? (si no, te invito a [ver este video en donde hablo sobre ellas](https://www.youtube.com/watch?v=Htsknf4L2o4)), entonces sabrás la importancia de estas para mantener un código limpio, estandarizado y entendible, principalmente cuando estamos trabajando en equipo. Una vez aceptada la necesidad de contar con una guía de estilo la pregunta puede ser ¿cuál aplicar?

Sin importar cuál elijas, ponerla en marcha en tu equipo puede tomar más tiempo de lo que podrías pensar, creo que esto sucede por diversos factores:

- Falta de práctica al usarla, es decir, la programadora no está familiarizado con las convenciones definidas, por lo tanto no las aplica.
- Falta de ejecución, es decir, aún si el programador no cumple con las reglas, no hay forma de avisarle que está rompiendo las convenciones adoptadas por el equipo.

Estas dos condiciones pueden inclusive llevar al fracaso de la implementación de una guía de estilo, pero, si solamente se trata de poner el código con un formato bien acordado, ¿por qué no podría ser una tarea que se realice de forma automática y sin tener que molestar al programador?

### Formateadores automáticos de código

Muchos lenguajes de programación cuentan ya con formateadores automáticos de código, que no hacen mas que justamente eso: aplicar cierto formato al código en un intento de reducir las tareas del programador o programadora, pues estos ya no se tienen que preocupar por asegurarse de escribir código que se vea "bonito", solamente deben preocuparse por escribir lógica que funciona y que sea entendible.

Ejemplos hay muchos, yo en particular tengo experiencia con [black](https://pypi.org/project/black/) y [flake8](https://flake8.pycqa.org/en/latest/), pero existen además herramientas para [Flutter](https://flutter.dev/docs/development/tools/formatting), [Prettier](https://prettier.io/) para JavaScript, [Java también tiene el suyo](https://github.com/google/google-java-format), también hay herramientas que soportan múltiples lenguajes como [ClangFormat](http://clang.llvm.org/docs/ClangFormat.html).

### Revisores automáticos de código

Al igual que es importante aplicar una guía de estilo, también es importante revisar que esta se haya aplicado correctamente. Por ejemplo, en el trabajo, ningún *pull request* llega a *"master"* sin asegurarnos de que se está siguiendo el estilo acordado. La forma en la que lo implementamos es que antes de comenzar a ejecutar las pruebas unitarias, ejecutamos dentro de nuestro *pipeline* la revisión automática y si no pasa ni nos molestamos en ejecutar los demás pasos.

Usualmente los formateadores automáticos también cuentan con herramientas que revisan que el código haya sido formateado correctamente, por ejemplo, si ejecutas *black* para Python con el argumento `--check`, este revisará que el código cumpla con sus estándares y si no, retornará un código de error.

## Pero, ¿qué hay de C#?

si bien hay diversas guías de estilo para C#, es difícil encontrar una herramienta que las aplique y las ejecute automáticamente; de mi exhaustiva investigación encontré cuatro herramientas:

- **El formateador automático de código incluido con Visual Studio**: A su favor tiene que viene por default dentro del editor de código, además de que, a pesar de ser muy básico, es configurable. En contra tiene el hecho de que no es multiplataforma, no tiene un para revisar automáticamente el estilo, ni es posible invocarlo desde la consola, haciendo que usarlo en un *pipeline* automatizado sea casi imposible.
- **El formateador de código incluido dentro del conjunto de herramientas de ReSharper**: es similar en *pros* al default incluido dentro de Visual Studio, sin embargo cuenta con más opciones y es más poderoso para analizar el código y dar mejores sugerencias. En contra tiene el hecho de que no es ejecutable desde la consola, además de que es necesario pagar para usarlo.
- **[CodeFormatter](https://github.com/dotnet/codeformatter)**: Un proyecto bastante interesante, patrocinado (y usado) por desarrolladores de la *.NET Platform*. A su favor tiene que navega bajo la bandera de *.NET*, y que es usado activamente por muchos desarrolladores dentro de productos muy conocidos. Me atrevería a decir que en contra tiene el hecho de que no es oficialmente multiplataforma, además de que no encontré como lograr de que se ejecute en modo revisión, para únicamente verificar el código escrito.
- **[StyleCop.Analyzers](https://github.com/DotNetAnalyzers/StyleCopAnalyzers)**: Este es un proyecto cuyo objetivo es dotar a nuestro editor de código y a la cadena de compilación de herramientas para analizar el código. A su favor tiene que podemos usarlo con solo instalar un paquete de NuGet, y que es multiplataforma (puesto que se instala directamente en nuestro proyecto de .NET). En su contra tiene que no es una herramienta invocable (al menos directamente) desde la consola, además de que no es tan personalizable como otras opciones.

## Usando StyleCop.Analyzers en .NET Core

Para uno de los proyectos más recientes en los que tuve que trabajar me decidí por la cuarta opción, acá te quiero contar cómo es que esta herramienta funciona y cómo es que la puedes usar en tus proyectos.

### 1. Agregando el analizador al proyecto

El primer paso es agregar el paquete `StyleCop.Analyzers` al proyecto que queremos analizar, para eso editamos el `.csproj` para agregarle estas líneas dentro del nodo `Project`:

```
<ItemGroup>
	<PackageReference  Include="StyleCop.Analyzers"  Version="1.1.118">
		<IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
		<PrivateAssets>all</PrivateAssets>
	</PackageReference>
</ItemGroup>

```

Puede que para el momento en que estés leyendo esto la versión *1.1.118* esté desactualizada, pero por eso no te preocupes todavía, después la puedes actualizar por una más reciente. Puedes ver el cambio en [esta *pull request*](https://github.com/ThatCSharpGuy/StyleCopTestProject/pull/1/files#diff-929525c6ea9e392036385e8b01191bc9R8-R13).

Desde ya puedes ver los resultados del paquete que recien instalamos, si abres el código en un editor como Visual Studio verás algo como lo siguiente:

![https://i.imgur.com/Dpaz7Qe.png](https://i.imgur.com/Dpaz7Qe.png)

Sí,

*Warnings*

por todos lados. Y todos esas advertencias vienen de

*StyleCop*

.

Pero no te preocupes si no tienes un editor, puesto que las *Warnings* aparecen también cuando intentas compilar el código:

![https://i.imgur.com/qr8Yx3e.png](https://i.imgur.com/qr8Yx3e.png)

### 2. Agregando un *ruleset*

Sí, sí, te entiendo... puede que muchas de esas advertencias no te interesen o te parezcan absurdas, así que el siguiente paso es encargarnos de ellas, para ello es necesario agregar un *ruleset* a nuestro proyecto. Este *ruleset* no es más que un archivo que le indica al compilador (y a nuestro entorno de programación) qué reglas debemos aplicar al código y qué severidad deben tener estas. Un buen lugar para comenzar es con un *ruleset* por default, puedes [usar este para comenzar](https://github.com/DotNetAnalyzers/StyleCopAnalyzers/blob/master/StyleCop.Analyzers/StyleCop.Analyzers.ruleset) o puedes crear el tuyo siguiendo la información en [este enlace](https://docs.microsoft.com/en-us/visualstudio/code-quality/how-to-create-a-custom-rule-set?view=vs-2019).

La estructura de este documento es algo así:

```xml
<?xml version="1.0" encoding="utf-8"?>
<RuleSet Name="Rules for StyleCop.Analyzers" Description="Code analysis rules for StyleCop.Analyzers.csproj." ToolsVersion="16.0">
  <Rules AnalyzerId="StyleCop.Analyzers" RuleNamespace="StyleCop.Analyzers">
    <Rule Id="SA1633" Action="Warning" />
    <Rule Id="SA0001" Action="Warning" />
    <Rule Id="SA1200" Action="Warning" />
    <!-- ... -->
    <Rule Id="SA1400" Action="Warning" />
  </Rules>
</RuleSet>
```

Aquí lo importante a notar es que cada `Rule` cuenta con un identificador y la severidad con la que el compilador nos debe presentar cualquier violación a esa regla. Para la severidad los valores posibles son estos: *Error*, *Warning*, *Info*, *Hidden* y *None* siendo *Error* la más grave y que simplemente no dejará compilar tu código, *Warning* mostrará mensajes como los que están arriba, y tanto *Hidden* como *None* suceden sin que nos enteremos.

### 3. Asignando nuestro *ruleset* al proyecto.

Supongamos que guardaste el achivo (con el nombre `project.ruleset`) con las reglas en el directorio raíz de tu proyecto, junto al archivo `sln`, el siguiente paso es ligar este con cada proyecto en el que queremos que se aplique, y para esto es necesario volver a editar el `csproj` para agregar las siguientes líneas:

```xml
  <PropertyGroup>
    <CodeAnalysisRuleSet>../project.ruleset</CodeAnalysisRuleSet>
  </PropertyGroup>
```

Puedes ver los cambios en [esta *pull request*](https://github.com/ThatCSharpGuy/StyleCopTestProject/pull/2/files).

### 4. Configurando las reglas.

Una vez que hayamos asignado nuestro *ruleset,* podemos comenzar a editarlo. Por ejemplo, digamos que no te la regla **SA1633: The file header is missing or not located at the top of the file.**, para deshabilitarla debemos buscar dentro de nuestro set de reglas el nodo `Rule` con el `Id` **SA1633** y cambiar el valor de `Action` de *Warning* a *None:* 

```xml
<Rule Id="SA1633" Action="None" />
```

Y supongamos que tienes fuertes opiniones sobre el hecho de que tanto clases como métodos declaren su accesibilidad explícitamente. Es decir, la regla **SA1400,** una forma de forzar a que esta regla sea respetada es haciendo que la compilación falle, logramos esto cambiando nuevamente el *ruleset*:

```xml
<Rule Id="SA1400" Action="Error" />
```

Ahora, si intentamos compilar el proyecto sin corregir errores, verás en la pantalla algo así:

![https://i.imgur.com/7pNFDHL.png](https://i.imgur.com/7pNFDHL.png)

Como puedes la advertencia **SA1633** ha desaparecido, mientras que **SA1400** pasó de ser un simple *Warning* a ser un error de compilación que impedirá que el código sea compilado. Y pues en un proyecto con un flujo de trabajo bien establecido el código que no compila, no llega a la rama productiva.

### 5. Componiendo los errores

Una vez que hemos logrado molestar al desarrollador o desarrolladora con su código incompilable por errores "estéticos" es su tarea componerlos... ¿o no? Pues *NO,* al menos si estás usando un editor de texto como Visual Studio (ya sea el de Mac o Windows, cualquiera en su versión gratuita).

Para muestra, mira la siguiente captura de pantalla:

![https://i.imgur.com/5CDYCdn.gif](https://i.imgur.com/5CDYCdn.gif)

El mismo editor nos dice cuál es el error y nos da sugerencias para corregirlo automáticamente. Y, si estás utilizando Visual Studio para Windows, podrás aplicar las sugerencias a todos los documentos del proyecto o, inclusive, de la solución.

## Conclusiones sobre StyleCop.Analyzers

¿Es molesto? **Sí, al inicio**, conforme escribes más código te vas acostumbrando a escribirlo de forma "correcta" adhiriéndote a la guía de estilo; idealmente llegará en un momento en el que las sugerencias sean mínimas puesto que ya estarás aprendiendo.

¿Es la forma correcta de aplicar una guía de estilo? **No me parece lo ideal pero sí una de las mejores maneras**, se me hace un tanto agresivo el hecho de provocar que el código no compile por el más mínimo error estético; pero de igual manera: tu código no compilaría si tuvieras cualquier otro error sintáctico.

¿Lo recomiendo? **Por supuesto que sí**, lo recomiendo y lo uso en todos los proyectos que puedo.

Espero que este post the haya sido de utilidad, y si tienes dudas o comentarios, me puedes preguntar en [Twitter](https://twitter.com/io_exception). 
