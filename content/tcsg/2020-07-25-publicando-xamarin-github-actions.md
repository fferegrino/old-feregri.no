---
layout: post
lannguage: es
title: Publicando aplicaciones hechas con Xamarin desde GitHub Actions
date: 2020-07-25 12:00:00
author: Antonio Feregrino
short_summary: ¿A quién no le gusta el código escrito siguiendo un estandar? te muestro como puedes aplicar el tuyo en .NET
lang: es
tags: c-sharp, Windows
---

### Requerimientos  
En este caso, vamos a usar *GPG* para protegerlos, si no tienes `gpg` instalada en tu Mac, la puedes instalar con `
brew install gpg`.

Una contraseña (vamos a llamarla `DECRYPT_KEY`) para encriptar archivos mediante *gpg*, te recomiendo que sea generada automáticamente. Genérala y tenla a la mano porque la vamos a utilizar unas cuantas veces en este post.

### Obteniendo un certificado de publicación para iOS  
Te recomiendo generar un certificado de publicación para cada app que desarrolles, aunque, este certificado lo puedes compartir entre varias, puesto que este certificado te identifica a ti como quien publica la app. En este caso, será el servidor de GitHub el que publique y al que tu le estarás dando permiso de autenticarse como tu.

Para generar un certificado nuevo, visita https://developer.apple.com/account/resources/certificates/list, elige "Crear un nuevo certificado" y selecciona "Apple Distribution":

![Imgur](https://imgur.com/b6T6YYw.png)
Una vez creado, descarga el certificado e instálalo en tu computadora. Para instalarlo simplemente da doble click en el archivo que acabas de descargar.

![Imgur](https://i.imgur.com/XXThK37.png)
El siguiente paso es crear y descargar un perfil de publicación para tu app:

![Imgur](https://i.imgur.com/6CodfmN.png)
Elige "Distribution" y "App Store":

![Imgur](https://i.imgur.com/TbrqVrY.png)
Elige después el identificador de tu aplicación:

![Imgur](https://i.imgur.com/0eCLTi0.png)
Asegurate también que elijas el certificado adecuado, justamente el que creamos en el paso anterior.

![Imgur](https://i.imgur.com/pIKkXbl.png)
Establece un nombre descriptivo, y genera el perfil de publicación.

![Imgur](https://i.imgur.com/peJlpOZ.png)
Siguiente paso es descargar y abrir el perfil de publicación, si Xcode no está abierto, el abrir el perfilde publicación lo abrirá. Una vez hecho esto, podemos configurar nuestra app para usarlos al momento de crear el archivo que vamos a publicar en la app store.

## Configura tu app para usar los certificados  
El siguiente paso es configurar tu aplicación de Xamarin.iOS (o tu aplicación de iOS normal), la opción a elegir en Xamarin es "iOS Bundle Signing", asegurate de que en la Configuración esté seleccionada la opción `Release` y de que como plataforma esté elegida `iPhone`. Luego entonces selecciona el certificado y el perfil de aprovisionamiento que acabamos de crear.

![Imgur](https://i.imgur.com/zJGWRBu.png)


## Colocando los certificados en GitHub
 > 🚨⚠️ ¡Mucho cuidado! ¡asegúrate de no subir ninguno de los siguientes archivos a menos de que estén encriptados! ⚠️🚨

### Exportando el certificado  
![Imgur](https://i.imgur.com/G0pF2C0.png)
![Imgur](https://i.imgur.com/hByhz7g.png)
Guarda el archivo con el nombre `Certificates.p12` dentro de la carpeta `secrets`.

![Imgur](https://i.imgur.com/5gT22K6.png)
### Exportando los perfiles de publicación  
Lo primero es descubrir cuál es el perfil de publicación que corresponde al que acabamos de descargar, para hacerlo, lista los perfiles con el siguiente comando:

```bash
ls -lah ~/Library/MobileDevice/Provisioning\ Profiles/
```

En este caso, el más reciente es el que corresponde al perfil de publicación de nuestra app, tiene el identificador `f3b9e904-6d99-409a-91f4-440c5b79565d`:

![Imgur](https://i.imgur.com/9cEkq9v.png)
El siguiente paso es copiar el perfil a la carpeta `secrets`. 

```bash
cp ~/Library/MobileDevice/Provisioning\ Profiles/f3b9e904-6d99-409a-91f4-440c5b79565d.mobileprovision secrets
```

Toma nota de este identificador porque lo verás en muchos lados, el mío es `f3b9e904-6d99-409a-91f4-440c5b79565d` pero el tuyo sera diferente.

### Encriptando nuestros secretos  
Como lo mencioné al inicio de esta sección, no podemos subir nuestros secretos (léase el certificado y el perfil de publciación) así como así a GitHub, antes hay que protegerlos mediante la encriptación. Usaremos *gpg* y la contraseña que creaste al inicio de este post.

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

### Desencriptando el acertificado en GitHub  
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

 -  Establece el Keychain recien creado como default

```bash
security list-keychains -s ~/Library/Keychains/build.keychain
security default-keychain -s ~/Library/Keychains/build.keychain
security unlock-keychain -p "" ~/Library/Keychains/build.keychain
security set-key-partition-list -S apple-tool:,apple: -s -k "" ~/Library/Keychains/build.keychain
```

Todas las instrucciones anteriores debemos colocarlas en un archivo llamado `decrypt_secrets.sh` dentro de nuestra carpeta `secrets`, no te olvides de darle permisos de ejecución a este archivo mediante el siguiente comando:

```bash
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

![Imgur](https://imgur.com/AP4VRrl.png)
Hay que añadir tres nuevos secretos:  

 - `DECRYPT_KEY`: la contraseña que usamos para encriptar los secretos
 - `APPLEID_USERNAME`: la cuenta de correo electrónico para acceder a iTunes Connect (para mayor seguridad, puedes crear una cuenta de correo específica para cada app)
 - `APPLEID_PASSWORD`: la contraseña de la cuenta de iTunes Connect
