---
layout: post
lannguage: es
title: Publicando aplicaciones hechas con Xamarin desde GitHub Actions
date: 2020-07-25 12:00:00
original_url: https://thatcsharpguy.com/post/publicando-aplicaciones-hechas-con-xamarin-desde-github-actions
author: Antonio Feregrino
short_summary: Aplica la integración continua a tus aplicaciones hechas con Xamarin y publica desde GitHub Actions.
lang: es
social_image: https://i.imgur.com/zGD1Caj.png
tags: xamarin, xamairn-forms, github, github-actions
---

La combinación de integración y despliegue continuo es fantástica, no hay nada mejor que la sensación de saber que tus cambios estarán en producción tan rápido como sea posible; además de evitarte el tedio de tener que hacer el *deployment* manualmente, que en el caso de Xamarin.Forms es un doble dolor: publicar en la App Store y Google Play. 

En este pequeño tutorial les voy a mostrar cómo es que podemos usar las herramientas a nuestro alcance para lograr simplificar el proceso de publicación de apps usando GitHub Actions; ahora, mientras que aquí hablo sobre Actions en específico, esto no implica que puedas llevar las mismas ideas a tu herramienta favorita de *CI*.

### Requerimientos  

Vamos a usar *GPG* para proteger los archivos necesarios para publicar, si no tienes `gpg` instalada en tu Mac, la puedes instalar con `
brew install gpg`. Idealmente cuentas con una Mac, sin embargo, no te preocupes si ese no es el caso, puedes continuar leyendo el tutorial y aplicar las ideas en tu computadora Windows.

Una contraseña (vamos a llamarla `DECRYPT_KEY`) para encriptar archivos mediante *gpg*, te recomiendo que sea generada automáticamente. Genérala y tenla a la mano porque la vamos a utilizar unas cuantas veces en este post.

Idealmente ya cuentas con conocimiento de cómo publicar tus apps en las tiendas.

# iOS

## Obteniendo un certificado de publicación para iOS  
Te recomiendo generar un certificado de publicación para cada app que desarrolles, aunque, este certificado lo puedes compartir entre varias, puesto que este certificado te identifica a ti como quien publica la app. En este caso, será el servidor de GitHub el que publique y al que tú le estarás dando permiso de autenticarse como tu.

 - Para generar un certificado nuevo, visita [https://developer.apple.com/account/resources/certificates/list](https://developer.apple.com/account/resources/certificates/list), elige "Crear un nuevo certificado" y selecciona "Apple Distribution":

![elige "Crear un nuevo certificado" y selecciona "Apple Distribution"](https://imgur.com/b6T6YYw.png)

 - Una vez creado, descarga el certificado e instálalo en tu computadora. Para instalarlo simplemente da doble click en el archivo que acabas de descargar.

![descarga el certificado e instálalo en tu computadora](https://i.imgur.com/XXThK37.png)

 - El siguiente paso es crear y descargar un perfil de publicación para tu app:

![El siguiente paso es crear y descargar un perfil de publicación para tu app](https://i.imgur.com/6CodfmN.png)

 - Elige "Distribution" y "App Store":

![Elige "Distribution" y "App Store"](https://i.imgur.com/TbrqVrY.png)

 - Elige después el identificador de tu aplicación:

![Elige después el identificador de tu aplicación](https://i.imgur.com/0eCLTi0.png) 

 - Asegúrate también que elijas el certificado adecuado, justamente el que creamos en el paso anterior.

![Asegúrate también que elijas el certificado adecuado](https://i.imgur.com/pIKkXbl.png)

 - Establece un nombre descriptivo, y genera el perfil de publicación.

![Establece un nombre descriptivo, y genera el perfil de publicación](https://i.imgur.com/peJlpOZ.png)

 - El siguiente paso es descargar y abrir el perfil de publicación, si Xcode no está abierto, el abrir el perfilde publicación lo abrirá. Una vez hecho esto, podemos configurar nuestra app para usarlos al momento de crear el archivo que vamos a publicar en la App Store.

## Configura tu app para usar los certificados  
 El siguiente paso es configurar tu aplicación de Xamarin.iOS (o tu aplicación de iOS normal), la opción a elegir en Xamarin es "iOS Bundle Signing", asegúrate de que en la Configuración esté seleccionada la opción `Release` y de que como plataforma esté elegida `iPhone`. Luego entonces selecciona el certificado y el perfil de aprovisionamiento que acabamos de crear.

![Configura tu app para usar los certificados](https://i.imgur.com/zJGWRBu.png)


## Colocando los certificados en GitHub  

 > 🚨⚠️ ¡Mucho cuidado! ¡asegúrate de no subir ninguno de los siguientes archivos a menos de que estén encriptados! ⚠️🚨

### Exportando el certificado  

![Exportando el certificado](https://i.imgur.com/G0pF2C0.png)  

![Exportando el certificado](https://i.imgur.com/hByhz7g.png)  

Guarda el archivo con el nombre `Certificates.p12` dentro de la carpeta `secrets`.

![Guarda el archivo con el nombre Certificates.p12 dentro de la carpeta secrets](https://i.imgur.com/5gT22K6.png)

### Exportando los perfiles de publicación  
Lo primero es descubrir cuál es el perfil de publicación que corresponde al que acabamos de descargar, para hacerlo, lista los perfiles con el siguiente comando:

```bash
ls -lah ~/Library/MobileDevice/Provisioning\ Profiles/
```

En este caso, el más reciente es el que corresponde al perfil de publicación de nuestra app, tiene el identificador `f3b9e904-6d99-409a-91f4-440c5b79565d`:

![En este caso, el más reciente es el que corresponde al perfil de publicación de nuestra app](https://i.imgur.com/9cEkq9v.png)  

El siguiente paso es copiar el perfil a la carpeta `secrets`. 

```bash
cp ~/Library/MobileDevice/Provisioning\ Profiles/f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision secrets
```  

Toma nota de este identificador porque lo verás en muchos lados, el mío es `f3b9e904-6d99-409a-91f4-440c5b79565d` pero el tuyo sera diferente.

### Encriptando nuestros secretos  

Como lo mencioné al inicio de esta sección, no podemos subir nuestros secretos (léase el certificado y el perfil de publicación) así como así a GitHub, antes hay que protegerlos mediante la encriptación. Usaremos *gpg* y la contraseña que creaste al inicio de este post.

```bash
gpg --symmetric --cipher-algo AES256 Certificates.p12
gpg --symmetric --cipher-algo AES256 f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision
```

Después de esto, deberás tener un par de archivos con el mismo nombre que los anteriores, pero con `.gpg` como extensión:

```bash
Certificates.p12.gpg
f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision.gpg
```

Solo para asegurarnos de que no vamos a publicar nuestros secretos al descubierto, los eliminamos:

```bash
rm Certificates.p12
rm f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision
```

### Desencriptando el certificado en GitHub  
Una vez que nuestros archivos están en GitHub encriptados, debemos hacer posible desencriptarlos dentro de la ejecución de nuestro flujo de trabajo:  

 - Desencriptar los secretos usando el password almacenado en "DECRYPT_KEY"
 
```bash
gpg --quiet --batch --yes --decrypt --passphrase="$DECRYPT_KEY" --output ./secrets/f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision ./secrets/f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision.gpg
gpg --quiet --batch --yes --decrypt --passphrase="$DECRYPT_KEY" --output ./secrets/Certificates.p12 ./secrets/Certificates.p12.gpg
```
 - Crea la carpeta "Provisioning Profiles" en la computadora que está ejecutando las acciones de GitHub

```bash
mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
```

 - Copia el perfil de publicación a la carpeta recién creada

```bash
cp ./secrets/f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision ~/Library/MobileDevice/Provisioning\ Profiles/f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision
```

 - Crea un Keychain e importa el archivo Certificates.p12

```bash
security create-keychain -p "" build.keychain
security import ./secrets/Certificates.p12 -t agg -k ~/Library/Keychains/build.keychain -P "" -A
```

 - Establece el Keychain recien creado como default

```bash
security list-keychains -s ~/Library/Keychains/build.keychain
security default-keychain -s ~/Library/Keychains/build.keychain
security unlock-keychain -p "" ~/Library/Keychains/build.keychain
security set-key-partition-list -S apple-tool:,apple: -s -k "" ~/Library/Keychains/build.keychain
```

Todas las instrucciones anteriores debemos colocarlas en un archivo llamado `decrypt_secrets.sh` dentro de nuestra carpeta `secrets`, no te olvides de darle permisos de ejecución a este archivo mediante el siguiente comando:

```
chmod +x secrets/decrypt_secrets.sh
```  

## Compilando la app  
El siguiente paso en el flujo de trabajo es compilar la aplicación de tal modo que nos genere un archivo `.ipa` que podemos cargar directamente en la App Store, para esta tarea usaremos `msbuild`:  

```bash
nuget restore
msbuild \
  /p:Configuration=Release \
  /p:Platform=iPhone \
  /p:BuildIpa=true \
  /target:Build \
  PinCountdown.iOS/PinCountdown.iOS.csproj
```
Primero estamos restaurando todos los paquetes de NuGet, luego le indicamos que queremos compilar la aplicación usando la configuración `Release`, además de que queremos que compile el archivo Ipa, y lo apuntamos al proyecto de iOS, que en mi caso está en `PinCountdown.iOS/PinCountdown.iOS.csproj`.

## Publicando en iTunes Connect  
El siguiente paso es publicar nuestro archivo `.ipa` en la App Store, para ello vamos a usar una herramienta que nos ofrece Xcode:  

```bash
xcrun altool --upload-app -t ios \
  -f PinCountdown.iOS/bin/iPhone/Release/PinCountdown.iOS.ipa \
  -u "${{ secrets.APPLEID_USERNAME }}" -p "${{ secrets.APPLEID_PASSWORD }}"
```  

Le estamos indicando a `xcrun` que nuestro archivo a subir está en al carpeta `PinCountdown.iOS/bin/iPhone/Release/`, además de indicarle nuestras credenciales mediante secretos de GitHub, de los cuales hablaremos a continuación.

## Configurando GitHub  
Ahora, es necesario configurar nuestro repositorio con los secretos que vamos a usar para publicar nuestra app, para esto nos dirigimos a *Configuración > Secretos*

![Ahora, es necesario configurar nuestro repositorio con los secretos que vamos a usar para publicar nuestra app, para esto nos dirigimos a *Configuración > Secretos*](https://imgur.com/AP4VRrl.png)
Hay que añadir tres nuevos secretos:  

 - `DECRYPT_KEY`: la contraseña que usamos para encriptar los secretos
 - `APPLEID_USERNAME`: la cuenta de correo electrónico para acceder a iTunes Connect (para mayor seguridad, puedes crear una cuenta de correo específica para cada app)
 - `APPLEID_PASSWORD`: la contraseña de la cuenta de iTunes Connect

# Android  

## Generando una `keystore` 
Vamos a generar un primer APK de nuestra app porque hay que subir primero na versión manualmente (gracias Google), y de paso generamos un nuevo `keystore`.  Ojo que si ya publicaste una versión de tu app usando otro `keystore`, ese es el que debes usar en lugar de generar uno nuevo.

 - Da click derecho en tu aplicación de Xamarin.Android y selecciona *"Archivar para publicación"*

![Da click derecho en tu aplicación de Xamarin.Android y selecciona *"Archivar para publicación"*](https://imgur.com/3egO8Q0.png)
 - Una vez terminada la compilación, da click derecho en el archivo recién creado y selecciona *Firmar y distribuír*

![Una vez terminada la compilación, da click derecho en el archivo recién creado y selecciona *Firmar y distribuír*](https://i.imgur.com/2hk1gX0.png)  

 - Selecciona el método de distribución *Ad Hoc*

![Selecciona el método de distribución *Ad Hoc*](https://i.imgur.com/rsVmRGw.png)  

 - Para crear una nueva *keystore*, selecciona *Crear una nueva llave*  

![Para crear una nueva *keystore*, selecciona *Crear una nueva llave*](https://i.imgur.com/P7g1BFz.png)  

 - En la siguiente ventana, selecciona un alias para tu *keystore*, establece un alias y una contraseña, recuerda esta contraseña, vamos a llamarla `KEYSTORE_PASS`

![En la siguiente ventana, selecciona un alias para tu *keystore*, establece un alias y una contraseña](https://i.imgur.com/jwfIDZ3.png)  

 - Una vez creada, da click derecho para ver mayor información sobre la llave que acabas de crear

![Una vez creada, da click derecho para ver mayor información sobre la llave que acabas de crear](https://i.imgur.com/9254zZ4.png)  

 - Toma nota de la dirección de tu *keystore*, la vamos a usar más adelante
 
![Toma nota de la dirección de tu *keystore*, la vamos a usar más adelante](https://i.imgur.com/oKRhomm.png)  

 - Por último, continua con la publicación natural de tu app y cárgala a la Google Play Store, recuerda que es necesario publicar la primera versión manualmente.

## Cargando la *keystore* a GitHub  
Al igual que como hicimos con nuestros certificados de iOS, es necesario que carguemos nuestra *keystore* a GitHub, desde luego, debemos protegerla primero usando *gpg*.

¿Recuerdas la dirección de la *keystore* que obtuvimos en el paso anterior? es hora de usarla para copiar la *keystore* en nuestra carpeta `secrets`:

```bash
cp /Users/antonioferegrino/Library/Developer/Xamarin/Keystore/PinCountdown/PinCountdown.keystore ./secrets/PinCountdown.keystore
```

Encriptamos, usando nuevamente nuestra contraseña `DECRYPT_KEY` que generamos al incio:

```bash
cd secrets
gpg --symmetric --cipher-algo AES256 PinCountdown.keystore
```

Por último borramos el archivo `PinCountdown.keystore`, dejando solamente `PinCountdown.keystore.gpg` (además de los otros `.gpg` correspondientes a iOS):

```bash
rm PinCountdown.keystore
```

No te olvides de colocar tus cambios en GitHub, para que ahora tu *keystore* esté protegida dentro del control de versiones.

## Desencriptando la *keystore* en GitHub  

Coloca las siguientes líneas dentro del archivo `secrets/decrypt_secrets.sh` :

```bash
gpg --quiet --batch --yes --decrypt --passphrase="$DECRYPT_KEY" --output ./secrets/PinCountdown.keystore ./secrets/PinCountdown.keystore.gpg
```

## Compilando la app  

```bash
nuget restore
msbuild \
  /p:Configuration=Release \
  /p:Platform=AnyCPU \
  /target:SignAndroidPackage \
  /p:AndroidSigningKeyAlias="PinCountdown" \
  /p:AndroidSigningKeyPass='${{ secrets.KEYSTORE_PASS }}' \
  /p:AndroidSigningStorePass='${{ secrets.KEYSTORE_PASS }}'  \
  /p:AndroidKeyStore="true" \
  /p:AndroidSigningKeyStore="./secrets/PinCountdown.keystore" \
  PinCountdown.Android/PinCountdown.Android.csproj
```  

Con ese comando tan largo de *msbuild* le estamos indicando que queremos generar un paquete de Android en la configuración `Release`, junto con todos los detalles correspondientes a la *keystore* que vamos a usar para ese propósito.

## Cargando nuestro archivo a la Google Play Store  
Para este paso no es necesario hacer nada *"manualmente"*, solamente tenemos que usar la acción [r0adkll/upload-google-play@v1](https://github.com/r0adkll/upload-google-play) (que tendrás que configurar separadamente). El archivo de nuestro `apk` firmado está siempre dentro de la carpeta `bin/Release` del proyecto, en el caso de la app que he usado para este proyecto, el archivo está en: `PinCountdown.Android/bin/Release/com.messier16.pincountdown-Signed.apk`.

## Configurando GitHub  
En este último paso resta agregar un nuevo secreto, en esta ocasión el secreto `KEYSTORE_PASS`, que corresponde a la clave que establecimos en un paso anterior. Y listo, eso es todo para la configuración.

# Configurando GitHub actions

A continuación les muestro el archivo que pone todas las piezas en su lugar, esta es la configuración del *pipeline* de GitHub actions, en teoría, todos los pasos los describimos previamente y aquí solo resta usarlos.

```yaml
name: Build the app
on: push
jobs:
  build:
    runs-on: macOS-latest
    steps:

      - name: Checkout repo
        uses: actions/checkout@v1

      - name: Decrypt Secrets
        run: ./secrets/decrypt_secrets.sh
        env:
          DECRYPT_KEY: ${{ secrets.DECRYPT_KEY }}

      - name: iOS Build
        run: |
          nuget restore
          msbuild \
            /p:Configuration=Release \
            /p:Platform=iPhone \
            /p:BuildIpa=true \
            /target:Build \
            PinCountdown.iOS/PinCountdown.iOS.csproj

      - name: Android Build
        run: |
          nuget restore
          msbuild \
            /p:Configuration=Release \
            /p:Platform=AnyCPU \
            /target:SignAndroidPackage \
            /p:AndroidSigningKeyAlias="PinCountdown" \
            /p:AndroidSigningKeyPass='${{ secrets.KEYSTORE_PASS }}' \
            /p:AndroidSigningStorePass='${{ secrets.KEYSTORE_PASS }}' \
            /p:AndroidKeyStore="true" \
            /p:AndroidSigningKeyStore="$PWD/secrets/PinCountdown.keystore" \
            PinCountdown.Android/PinCountdown.Android.csproj

      - name: Save generated IPA
        uses: actions/upload-artifact@v2
        with:
          name: PinCountdown.iOS.ipa
          path: PinCountdown.iOS/bin/iPhone/Release/PinCountdown.iOS.ipa

      - name: Save generated APK
        uses: actions/upload-artifact@v2
        with:
          name: PinCountdown.Android.apk
          path: PinCountdown.Android/bin/Release/com.messier16.pincountdown-Signed.apk

      - name: Publish to App Store
        run: |
          xcrun altool --upload-app -t ios \
            -f PinCountdown.iOS/bin/iPhone/Release/PinCountdown.iOS.ipa \
            -u "${{ secrets.APPLEID_USERNAME }}" -p "${{ secrets.APPLEID_PASSWORD }}"

      - name: Publish to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.messier16.pincountdown
          releaseFile: PinCountdown.Android/bin/Release/com.messier16.pincountdown-Signed.apk
          track: alpha
```

Puedes ver todos los cambios que hice en [esta Pull Request](https://github.com/messier16/pin-countdown/pull/1/files).

## Errores comunes y consejos  

He de aceptarlo, poner todas las piezas juntas me costó un poco de trabajo, además de [consumir todos mis minutos disponibles en Actions](https://twitter.com/io_exception/status/1282370753279725570) porque estaba probando en un repositorio privado. Así que con el objetivo de hacer el proceso más sencillo para ti te dejo estos consejos:  

 - **Cada que vas a publicar en las tiendas, debes cambiar el número de versión de tu app**: Las tiendas de aplicaciones son muy estrictas en cuanto a las versiones que publicas de tu app, en el sentido de que no puedes publicar la misma versión dos veces. Te invito a que veas mi post sobre [cómo versionar cualquier app con Python](http://feregrino.dev/versioning-any-app-with-python.html) para que veas una manera de hacerlo automáticamente.

 - **Asegúrate de que el *pipeline*  que publica solamente se ejecute cuando quieres publicar**: si te fijas en el *yaml* anterior, tenemos configurado GitHub actions para que se ejecute cada vez que alguien hace *push* al repo, causando que estemos publicando nuestras apps constantemente; el problema es mayor si ignoramos el punto anterior (cada nueva publicación en las tiendas requiere una nueva versión). Una solución para este problema es la de solamente ejecutar este *pipeline* cuando etiquetamos un commit:  

```yaml
on:
  push:
    tags:
      - '*'
```  

  - **Guarda todas las contraseñas que uses**: no podrás recuperar ninguna contraseña de las que guardes como secretos de GitHub, es importante que las mantengas a salvo en otro lado en donde si las puedas recuperar.

## ¿Dudas?  
Encuéntrame en [https://twitter.com/io_exception](https://twitter.com/io_exception), en donde con todo gusto responderé cualquier duda que tengas.
