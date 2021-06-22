---
layout: post
language: es
title: Te cuento qué es MLOps
date: 2021-07-22 10:00:00
short_summary: MLOps es una nueva y emergente área de las ciencias de la computación que se ocupa de aplicar las mejores prácticas desarrollo de software a la puesta en producción de modelos de machine learning…
tags: mlops, data-science
original_url: https://medium.com/tacosdedatos/te-cuento-qu%C3%A9-es-mlops-3409055a9741
---  

# Te cuento qué esMLOps

MLOps es una nueva y emergente área de las ciencias de la computación que se ocupa de aplicar las mejores prácticas desarrollo de software a la puesta en producción de modelos de machine learning. Estas prácticas incluyen, pero no se limitan, a cosas como la colaboración en la escritura del código, pruebas automatizadas, reutilización de código, control de versiones, integración y despliegue continuos…  

La rama del MLOps requiere que los y las practicantes aprendan cómo construir un ciclo de vida de machine learning en donde tanto código, como nueva información es constantemente integrada a una aplicación. Todo esto sin perder de vista que en el centro de dicha aplicación existe un modelo no determinístico y que requiere de conocimiento especializado para ser mantenido, conocimiento que muchas veces está fuera del dominio ingenieril.  

 > Para comenzar a hacer MLOps tenemos que aceptar la premisa de que una aplicación exitosa de machine learning involucra muchos más componentes que el modelo estadístico que los y las científicas de datos crean.  

Tu trabajo, como ingeniero o ingeniera de MLOps es el dar soporte para que este modelo sea fácil de reentrenar, probar, desplegar y monitorear, todo esto con la finalidad de garantizar que su desempeño a través del tiempo se mantenga y siga sirviendo el propósito para el cual fue creado en primera instancia.

---

## El ciclo de vida de machine learning

Los y las practicantes de MLOps dedican gran parte de su tiempo a mantener el ciclo de vida del aprendizaje automático, ¿pero de qué se trata?

### Gestión de la información "cruda" y procesada  

Los datos son parte vital del machine learning es por eso que gestionarlos es de vital importancia. Y no solo se trata del manejo de bases de datos SQL o noSQL, sino también al uso de herramientas como las nuevas feature stores para almacenar información ya procesada por los científicos de datos, y otros sistemas de streaming que constantemente actualicen los datos a partir de lo que va sucediendo en producción.  

Aquí puede existir un pequeño traslape con las tareas de un ingeniero o ingeniera de datos.

### Desarrollo del modelo  

El tradicional desarrollo de la ciencia de datos que ya tanto conocemos, pero potenciada por un fuerte control de versiones que se extiende no solamente al código del modelo, sino también a todos los productos resultantes del entrenamiento.  

Además de buenas prácticas: seguir una guía de estilo en el código, contar con un nivel básico de pruebas… no ahondaré mucho en esto; en tacos de datos puedes encontrar más sobre esta etapa.

### Puesta en producción  

O la operacionalización (sí, el "ops" en MLOps"). La parte que se trata de colocar esa pieza de machine learning en el lugar adecuado, rodeado de otras piezas de software "tradicional".  

Aquí nos toca asegurarnos que cualquier sistema que alimente nuestro modelo, o se alimente de los resultados de este funciona correctamente a través de un conjunto sólido de pruebas (y no solo unitarias). Pero la cosa no se queda ahí, puesto que también es importante entender que el sistema requerirá de actualizaciones: ya sea que obtengamos más y mejores datos o que tengamos que hacer ajustes a otras partes dentro del código.  

Debemos considerar 3 cosas continuas: Integración, despliegue y entrenamiento continuos.

### Monitoreo  

Una vez que nuestra aplicación está en producción debemos poder estar monitoreándola constantemente. Recuerda que un modelo de aprendizaje automático captura una versión del mundo y el mundo está en constante cambio.  

 > Los modelos de *machine learning* son como los automóviles de agencia, en cuanto salen a la calle comienzan a perder su valor.  

No solo debemos mantener un ojo en el sistema completo, sino también la información que entra y sale del modelo de machine learning. Es importante darnos cuenta de cuándo es que este está comenzando a mostrar signos de degradación y tal vez mandar alguna alerta en un canal de Slack, encender una alarma en el lobby de tu compañía… o algo más avanzado y útil, como provocar que el modelo se entrene automáticamente.

### Conclusión  

Lo que te acabo de contar es un súper resumen de lo que implica el trabajo dentro de un proyecto en el que se está construyendo un sistema potenciado por aprendizaje automático.  

También cabe mencionar que se trata de un ciclo, no es un proceso que normalmente tenga un fin y habrá veces en que del desarrollo del modelo tengamos que regresar a la parte de almacenamiento y procesamiento de datos… y es muy común que el monitoreo nos motive a revisar la etapa de desarrollo del modelo. Se trata de recibir constante retroalimentación para mejorar nuestro producto.  

Ahora, sé que te gustaría que te hablara sobre las herramientas que se suelen usar dentro del MLOps y bueno, debes saber que existen muchas, literalmente cientos de herramientas que de una u otra forma están relacionadas con MLOps. En el futuro hablaré más a detalle sobre algunas de estas e inclusive te voy a mostrar un poco de código.  
