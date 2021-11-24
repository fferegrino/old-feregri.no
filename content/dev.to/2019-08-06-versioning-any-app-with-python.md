---
layout: post
language: en
original_url: https://dev.to/fferegrino/versioning-any-app-with-python-bij
title: Versioning any app with Python
date: 2019-08-06 14:00:00
tags: xamarin, python
short_summary: Learn how to version any app, any language, with python.
---  

I'm not here to lecture about the benefits of using [SemVer](https://semver.org/), and yes, I know SemVer is not very recommended for apps that do not expose a public API. However, in this post, I'll try to show you how to version your Xamarin.Forms app using Python and git. If you are not coding Xamarin apps, I hope you keep on reading as you can apply these principles to any other app in any language you use. 


As I said, we'll be using git and Python, so I'll assume you have a working installation of git, and Python with Pip.

### First our *"any"* app

The file where the version resides in Android is in the `AndroidManifest.xml` file:

```xml  
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" 
          android:versionCode="1" 
          android:versionName="0.0.0" 
          package="com.companyname.xamarinsemver">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="28" />
    <application android:label="XamarinSemVer.Android"></application>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
</manifest>

```  
You can see them in the attributes `android:versionName` for the version of the app, and `android:versionCode` for the *"build"*.

And in iOS, the version is stored in the `Info.plist` file: 

```xml
<!-- ... -->
<key>CFBundleVersion</key>
<string>1</string>
<key>CFBundleShortVersionString</key>
<string>0.0.0</string>
<!-- ... -->
```  
Here you can distinguish them as the value that follows `CFBundleVersion` for the *"build"* and the one that follows `CFBundleShortVersionString` for the version.

For this post I've set them both to `1` and `0.0.0`, it does not really matter if you are starting from scratch, **as long as both numbers in both projects match each other**.

All good and all with the Xamarin.Forms app. Now, the Python bits.

### Actual Python  

Now, the first step is opening a terminal (I prefer PowerShell) and install the package **advbumpversion**.

```shell
pip install advbumpversion
```

Of course, it is better if you do this using a virtual environment, [ask me how on twitter](https://twitter.com/io_exception).

### Configuring the versions  
Now, there is a configuration file that we must add to our project, this file holds the metadata for our versioning, as well as how the tool we just installed should behave. This file is named `.bumpversion.cfg` and should be located in the root of your project. Let's dive into its contents:

```text
[bumpversion]
current_version = 0.0.0-1
serialize = {major}.{minor}.{patch}-{build}
parse = (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)-(?P<build>\d+)
commit = True
tag = True
```

Let's go line by line:  

 1. `[bumpversion]`: just to denote that the configuration starts there
 2. `current_version = 0.0.0-1`: as it states, this is the current version, in the case of the app I created above, this starts at. Now, the key is that this number is not just *semver*, but *semver* plus the build number, separated by a hyphen.
 3. `serialize = {major}.{m...`: this line specifies what each part of the version mean for the tool  
 4. `parse = (?P<major>\d+)...`:  this tells bumpversion how to parse the version number we just provided
 5. `commit = True`: a boolean value that indicates whether a git commit should be created when bumping a version
 6. `tag = True`: a boolean value that indicates whether a tag to identify the current version should be created when bumping a version  

By this point you should be able to execute `bump2version --dry-run --verbose` and get something like this:  

```text
Parsing version '0.0.0-1' using regexp '(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)-(?P<build>\d+)'                                                                             
Parsed the following values: build=1, major=0, minor=0, patch=0   
```     

Now, it is our turn to tell the tool where to search for the versions inside our source code in order to replace them for us:

```text  
[bumpversion:file:XamarinSemVer\XamarinSemVer.iOS\Info.plist:0]
serialize = {major}.{minor}.{patch}
search = <string>{current_version}</string>
replace = <string>{new_version}</string>
```

Again, line by line:

 1. `[bumpversion:file:AgenteMovil.iOS/Info.plist:0]`: with this line we specify which file should be modified... that `:0` at the end? that just means that this is not the only time we are going to modify this file; you'll see later.
 2. `serialize = {major}.{minor}.{patch}`: this tells *bumpversion* that for the purpose of this configuration section, the version is formed only by *major*, *minor* and *patch* leaving *build* out of the play.
 3. `search = <string>{current_version}</string>`: the string to be replaced, in our first execution the tool will search for *"\<string>0.0.0\</string>"*
 4. `replace = <string>{new_version}</string>`: the string to be used to replace the above value, if we are increasing the major component, the replacement will look something like this: *"\<string>1.0.0\</string>"*  

Let's dissect the next piece of configuration

```text  
[bumpversion:file:XamarinSemVer\XamarinSemVer.iOS\Info.plist:1]
serialize = {build}
search = <string>{current_version}</string>
replace = <string>{new_version}</string>
```

There are just a couple of differences between this and the previous block of configuration:   
 - The `:1` at the end of the file specification, as I mentioned early, this is necessary to tell the tool that this is the second time we are going to touch this file.   
 - The value of `serialize`, this time it is set just to *build* since in this section we only care about the *build* number , now instead of searching for  *"\<string>0.0.0\</string>"*, the tool will search for  *"\<string>1\</string>"*, for example.  

Almost the same configuration can be applied for Android, I won't go into detail line by line, but here it is:  

```text  
[bumpversion:file:XamarinSemVer\XamarinSemVer.Android\Properties\AndroidManifest.xml:0]
serialize = {major}.{minor}.{patch}
search = android:versionName="{current_version}"
replace = android:versionName="{new_version}"

[bumpversion:file:XamarinSemVer\XamarinSemVer.Android\Properties\AndroidManifest.xml:1]
serialize = {build}
search = android:versionCode="{current_version}"
replace = android:versionCode="{new_version}"
```   

And finally, a critical piece of configuration. In the case of iOS and Android, the build number should always increase regardless of the version number. By default, *bumpversion* will reset the build number every time we increase any of the other numbers in our semver, the good news is that we can override this setting by including these lines in the configuration file:  

```text  
[bumpversion:part:build]
independent = True
```  

### Bumping versions (finally!)  

After all the hassle of installing and configuring, we are ready to begin bumping versions like crazy to keep our software better organised. Say you just fixed a bug in your codebase; you should do something like the following to bump the version:  

```shell
bumpversion build --no-tag  
bumpversion patch  
git push --follow-tags
```  

Line by line:  

 1. First, we increase the build, the argument `--no-tag` will override our configuration, since you may not want to create a tag when bumping build numbers.
 2. Then we increase a number in our *semver* scheme, depending on the type of change we made.
 3. We commit the files and the tags (with `--follow-tags`) to our repository and... that's it.

This will generate exactly two commits and a new tag in our repo, something like this:  

![Commit and tags](https://thepracticaldev.s3.amazonaws.com/i/c784wykevy23itlc0lx4.PNG)  

### Icing on the cake  

You could keep executing those three commands every time something worthy changes in your app... or you could use a *Makefile* to further automate the task, or to prevent tags from being pushed to other branches than *"master"*. Feel free to [peek at the *Makefile*](https://github.com/ThatCSharpGuy/xamarin-semver/blob/master/Makefile) I made, or why not? to the [full repository](https://github.com/ThatCSharpGuy/xamarin-semver).
