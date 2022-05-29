---
layout: post
language: en
original_url: https://dev.to/fferegrino/my-basic-windows-setup-4gdh
title: My basic Windows setup 
date: 2019-08-19 14:00:00
tags: windows, git, python, chocolatey
short_summary: Even though lately I've been using more and more Linux platforms, a part of me is still bound to Visual Studio and Windows; however, I do not let this stop me from doing Python development in almost the same way as I do in my Ubuntu partition.
---  

Even though lately I've been using more and more Linux platforms, a part of me is still bound to Visual Studio and Windows; however, I do not let this stop me from doing Python development in almost the same way as I do in my Ubuntu partition.  

That is why I set out to create this **simple** guide, for those who are interested in using Python in Windows with a certain degree of control. Plus, I'm sure I'll forget how to do this by the next time I format my computer, so this is also for the Me of the future.  

## Chocolatey  
Chocolatey is *"a package manager for Windows (like apt-get or yum but for Windows)"*, and I'll be using it to install `git` and `make`. I use Git for version control and Make to *"automate"* the somewhat tedious tasks.

To install Chocolatey, start PowerShell with administrative rights and paste this command:  
```shell  
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```
Be wary of all the commands you are asked to paste in your PS terminal! Please double-check the [command here](https://chocolatey.org/docs/installation#install-with-powershellexe).  

### Installing tools  
Now, once Chocolatey is installed, close PowerShell and start it again with administrative rights. Only to paste the following command to install both `make` and `git`:  

```shell  
choco upgrade make git -y
```

The `-y` in between is because I don't want *choco* to ask me for confirmation... I know what I'm doing.

Once the installation finishes, you should be able to type `make` in PS and see something like this:  

```shell
make: *** No targets specified and no makefile found.  Stop.
```

## Python  
To install Python you have to head to the [Python downloads](https://www.python.org/downloads/), you can choose whichever version you want; I opted for [Python 3.6.8]([https://www.python.org/downloads/release/python-368/](https://www.python.org/downloads/release/python-368/)), I downloaded the Windows x86-64 executable installer.  

Once executed, the installer will present you with a window like this:    

![https://i.imgur.com/Isdjhzd.png](https://i.imgur.com/Isdjhzd.png)

In this case, I selected *Install Now*, and I made sure to take note of the path displayed in there. Once the installation is done, I had to edit the environment variables, to make them point to where Python was installed, to do this one needs to modify the `Path` environment variable as follows:  

![enter image description here](https://i.imgur.com/1WstUpH.png)

The new paths are:  

 - `%USERPROFILE%\AppData\Local\Programs\Python\Python36`
 - `%USERPROFILE%\AppData\Local\Programs\Python\Python36\Scripts`  

By all means, you should make sure that the path ending in `WindowsApps` is below the new Python paths.  

Now, you should be able to use Python from the terminal (or PowerShell), type `python` and see something simiar to this output:  

```shell
Python 3.6.8 (tags/v3.6.8:3c6b436a57, Dec 24 2018, 00:16:47) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
```

### `pipenv`  
Once you have Python installed one is almost ready to go to code, but to keep a neat installation, and to isolate each one of our different projects it is recommended to use a virtual environment manager, and that is what *Pipenv* is for. To install it, paste the following command in your command line:

```shell  
pip install --user pipenv
```

This will install `pipenv`, but we are still a step away from being able to use it. Since we used the `--user` flag, the package was installed in a different location that we need to add to our path, very similarily as to what we had to do when installing Python.

The paths to add is:
 - `%USERPROFILE%\AppData\Roaming\Python\Python36`
 - `%USERPROFILE%\AppData\Roaming\Python\Python36\Scripts`

Make sure they are at the top, even after the original Python paths.  

## Additional tools  
There are other tools that I recommend installing, but these may be less important for you: 
 - [Visual Studio](https://visualstudio.microsoft.com/) 
 - [Visual Studio Code](https://code.visualstudio.com/)
 - [Notepad++](https://notepad-plus-plus.org/)  
 - [MobaXterm](https://mobaxterm.mobatek.net/) 
 - [Fiddler](https://www.telerik.com/fiddler)
 - [7-zip](https://www.7-zip.org/download.html)

I hope this post has been helpful, if you have questions or doubts, ask me on [Twitter](https://twitter.com/feregri_no).  
