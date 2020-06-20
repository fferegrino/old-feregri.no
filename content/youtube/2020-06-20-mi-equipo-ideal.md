---
layout: post
language: es
youtube: OWyZbIj9TCI 
title: Mi equipo ideal para desarrollo
date: 2020-06-22 10:00:00
short_summary: Les voy a hablar sobre lo que yo considero el entorno ideal para trabajar en equipo, no se trata de hablar directamente sobre programación, sino sobre muchos aspectos que en mi opinión, ayudan a que la programación sea más rápida, coordinada y sin tantas frustraciones cuando trabajamos en equipo.
tags: software-development, youtube
---

En esta transmisión en vivo, o video, si es que lo estás viendo después de grabado, les voy a hablar sobre lo que yo considero el entorno ideal para trabajar en equipo, no se trata de hablar directamente sobre programación, sino sobre muchos aspectos que en mi opinión, ayudan a que la programación sea más rápida, coordinada y sin tantas frustraciones cuando trabajamos en equipo.

El orden de los puntos sobre los que hablaré no tiene ningúna relación con su importancia y algunos de ellos están relacionados entre ellos.

## Control de versiones

El control de versiones es el pilar central, a partir de aquí parten casi todos los demás. El control de versiones da la certeza y garantía de todos los cambios realizados en el código de la aplicación están siendo almacenados y siempre se puede revisar quién hizo qué y cuando. En mi caso prefiero Git.

Existen diversos flujos de trabajo que puedes emplear usando Git: [https://www.atlassian.com/git/tutorials/comparing-workflows](https://www.atlassian.com/git/tutorials/comparing-workflows), [https://guides.github.com/introduction/flow/](https://guides.github.com/introduction/flow/), [https://nvie.com/posts/a-successful-git-branching-model/](https://nvie.com/posts/a-successful-git-branching-model/). Sin embargo el que yo uso más frecuentemente es el de las "*feature branches*" en el cual se tiene siempre una rama principal y cada nueva *feature* o característica, desde "cambia el texto de un botón" hasta, "haz que la aplicación mande correos a todos los miembros cada que alguien hace un cambio en esta orden", deben tener su propia rama.

Hay ocasiones en que el trabajo de una característica o funcionalidad no se puede realizar en una sola rama y entonces se recurre a otro flujo de trabajo en el que los cambios necesarios son integrados a una rama que no es la principal, para que, al final esta rama con un montón de integraciones (*commits* y *merge requests*) sea integrada finalmente a la rama principal.

Mi video sobre control de versiones: [https://youtu.be/Uts65gTG1k0](https://youtu.be/Uts65gTG1k0)

### Merge/pull requests

La forma de integrar los cambios de una rama a otra es mediante la realización de revisiones de código en pull (o merge requests dependiendo de la plataforma que uses). Hice todo un video sobre las revisiones de código, pero en síntesis, las revisiones de código nos dan la oportunidad de que revisar que lo que se esperaba de la funcionalidad está siendo implementada, también de que los estándares de código internos se están respetando; además de que son un medio más de comunicación entre los miembros del equipo. Otro de sus beneficios es que ayuda a repartir el conocimiento entre los compañeros, evitando tener un solo experto en cierta funcionalidad.

Mi video sobre *code reviews*: [https://youtu.be/Boaa3wDzPKE](https://youtu.be/Boaa3wDzPKE)

### Versionamiento

Siempre es una buena idea tener una forma de identificar qué versión de la aplicación está siendo ejecutada por el usuario, ya sea para que estos mismos sepan la compatibilidad de su software con otros elementos (por ejemplo, que la versión 7 de tu aplicación ya no es compatible con el iPhone X) o para cuando se trata de reportar errores, ya que el mismo usuario (o inclusive un sistema automatizado) puede reportarte que un error ocurrió en la versión 2.3.1 de tu app. Saber esta versión ayudará a que te sea más fácil encontrar la posible fuente del error. Independientemente de si estás desarrollando una aplicación móvil o una biblioteca que va a ser consumida por otros desarrolladores, te recomiendo que le eches un ojo al versionamiento semántico: [https://semver.org/](https://semver.org/) ([https://medium.com/@u_glow/making-sense-of-semantic-versioning-for-end-user-software-applications-a3049d97478b](https://medium.com/@u_glow/making-sense-of-semantic-versioning-for-end-user-software-applications-a3049d97478b), [https://softwareengineering.stackexchange.com/questions/318726/versioning-apps-with-semver](https://softwareengineering.stackexchange.com/questions/318726/versioning-apps-with-semver))

Mi video sobre versionamiento semántico: [https://youtu.be/dj8H2mqiAtU](https://youtu.be/dj8H2mqiAtU)

## Estándar de código

El primer paso es elegir un estándar de código y apegarse a él.

Sí, ya sé, somos individuos y cada uno tiene su forma de escribir código... sin embargo esto puede ser un problema al momento de integrar tus cambios con los de un compañero. Puede ser por que a ti te gusta escribir en nombre de las variables internas comenzando con mayúsculas y a los demás no, o porque tu no tienes problemas en leer un código que no tiene espacios entre los símbolos... de esto se trata el estándar, de obtener un código que de entrada, se vea uniforme; por ejemplo en donde sepas que si la variable comienza con guión bajo es porque es privada, o donde puedas inferir los tipos de retorno de un método dado su nombre.

[https://homes.cs.washington.edu/~mernst/advice/coding-style.html](https://homes.cs.washington.edu/~mernst/advice/coding-style.html)

Mi video sobre programar con estilo: [https://youtu.be/Htsknf4L2o4](https://youtu.be/Htsknf4L2o4)

## Visualización de quién está haciendo qué y por qué

En mi equipo siempre hay una forma de ver qué está haciendo cada uno, no es esto para tener a mis compañeros monitoreados, sino para saber qué tanto trabajo se puede asignar a cada uno, así evitamos sobrecargar a un desarrollador con más trabajo del que puede realizar y encima podemos ver más claro lo que se puede lograr y en cuanto tiempo.

Sí, sé que esto puede generar un poco de tensión en el equipo después de todo sentirse monitoreado no es una buena sensación... pero no se trata de eso, sino de organización, tanto para el proyecto como para cada miembro de el equipo. ¿No te ha pasado que te siguen amontonando y amontonando trabajo? estás desarrollando algo y llega alguien con un reporte sobre un error y te toca revisarlo... luego encima de eso la compilación está rota por un cambio en una librería. Creo yo que todo eso se elimina al momento en que puedes poner todo en un tablero y visualizar que tanta carga de trabajo tienes.

Y ojo que esto no tiene que ser un calendario detallado con cada hora de tu día laboral, basta con un tablero, como los esos tantos odiados de Jira, Trello o cualquier otro producto que te permita acomodar las tareas de forma que se vea un progreso a lo largo del tiempo.

GitHub boards: https://help.github.com/en/github/managing-your-work-on-github/about-project-boards#creating-and-viewing-project-boards

Jira: https:/www.atlassian.com/software/jira/scrum-boards

GitLab issue board: https://about.gitlab.com/stages-devops-lifecycle/issueboard/)

## Desarrollo local

Todo desarrollador debe poder trabajar localmente, y sin necesidad de conectarse a servicios externos (bases de datos, APIs de terceros). Docker es una gran herramienta para lograr esto. Una gran herramienta para esto, y si están trabajando con AWS, es LocalStack que nos ayuda a emular localmente estos servicios.

Esto nos ayuda a varias cosas:

Más rapidez para el desarrollador puesto que si todo está corriendo localmente se evita la conexión (y el retraso que eso significa). Obviamente esto depende mucho también de los recursos locales con los que cuente el desarrollador, es decir, no es lo mismo montar 10 contenedores en 4 gigas de RAM, que en 16.

Nos da más seguridad de que el código que estamos escribiendo funciona bajo los parámetros que nosotros establecimos; esto también ayuda a la rapidez del desarrollo.

Mayor seguridad en que lo que estamos desarrollando va a funcionar en producción.

Menor conflicto con el desarrollo de otros compañeros, si cada uno tiene su propio entorno, no hay posibilidad de que los cambios que introduce uno mientras desarrolla, afecten a los cambios que alguien más esté introduciendo en su trabajo.

El ideal es tener un entorno similar al que se tiene en producción pero ejecutándose en la computadora de cada desarrollador, pero cuando esto no es posible, se debe tratar de emular lo más posible.

## Pruebas, pruebas y pruebas

Debe haber pruebas para las partes más críticas de la aplicación, esto garantiza el funcionamiento de la aplicación cuando se introducen cambios. Todas las pruebas suman, aunque hay algunas que sumen menos que otras, idealmente comenzando por las unitarias y las de integración. El escenario ideal: tener pruebas de principio a fin para todos los procesos importantes.

Mi video sobre las pruebas unitarias: [https://youtu.be/8rKy1juvVmI](https://youtu.be/8rKy1juvVmI)

## Integración continua

Todos los cambios deben ser integrados constantemente a la aplicación y deberán ser automáticamente compilados y probados antes de hacerlo. Mediante esto estamos asegurándonos de que al menos, nuestro programa o aplicación compila. Si además complementamos esto con pruebas, es aún mejor porque de cierto modo estarás garantizando que además de compilar, tu aplicación está lista para funcionar al menos bajo los escenarios planteados en tus pruebas.

Mi video sobre integración continua: [https://youtu.be/58SjUKY6sKk](https://youtu.be/58SjUKY6sKk)

### Despliegue continuo

Si quieres puedes complementar la integración continua con algo conocido como despliegue continuo, que es es ir un paso más allá de la integración en donde cada vez que integras algo a cierto repositorio de código, este cambio es puesto inmediatamente en algun entorno para que los usuarios (ya sean finales o de QA) lo puedan usar.


