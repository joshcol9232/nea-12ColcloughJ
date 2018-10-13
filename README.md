# Dependencies:
- Python 3
- Kivy (install via pip):
  - Cython
  - sdl2/pygame (either is fine)
- PyBluez (install via pip):
  - Bluez devel package on linux

# Install on Linux
## All Distro's:
### Follow install process for kivy:
https://kivy.org/doc/stable/installation/installation-linux.html

### Also install:
```
pip3 install cython kivy pygame-(if no SDL2)
```
You might need some linux headers for PyBluez:
### Arch based next steps:
```bash
uname -r
```
To get kernel version, then:
```bash
sudo pacman -S base-devel linux-headers bluez-libs
sudo pip3 install pybluez
chmod +x /where-you-saved-it/code/python-go/AES
```
Then select appropriate headers for your kernel, and check you have appropriate graphics drivers installed (for OpenGL).
### Debian based next steps:
Tested on Ubuntu 18.04
```bash
uname -r
```
To get kernel version, then:
```bash
sudo apt-get update
sudo apt-get install linux-headers-<kernalversion> bluez libbluetooth-dev
sudo pip3 install pybluez
chmod +x /where-you-saved-it/code/python-go/AES
```
Then select appropriate headers for your kernel, and check you have appropriate graphics drivers installed (for OpenGL).
If you encounter an error regarding OpenGl try:
```bash
sudo apt-get install libglu1-mesa-dev freeglut3-dev mesa-common-dev
```

# Install On Windows
## Install Dependencies:

### Install Windows SDK for PyBluez if using bluetooth:
https://developer.microsoft.com/en-US/windows/downloads/windows-10-sdk

### Install pip modules:
```
cd /WherePythonIsInstalled/Scripts/
pip install cython pygame-(if needed) pybluez
```

### Follow install process for kivy:
https://kivy.org/doc/stable/installation/installation-windows.html

# Run program:
## Linux:
Execute in shell:
```bash
cd /WhereYouSavedIt/code/python-go/
(sudo) python3 start.py
```
Use sudo if you are using Bluetooth.

If you get a permissions error, make sure /WhereYouSavedIt/code/python-go/AES is executable. If it isn't, run:
```bash
chmod +x /WhereYouSavedIt/code/python-go/AES
```

If it crashes on start-up make sure your config file is configured correctly.

## Windows:
Go to **WhereYouSavedIt --> code --> python-go** and open start.py with Python 3.X.

If it crashes on start-up make sure your config file is configured correctly.


# The App:
Since the app is not (yet) available on the Google play store, you have to build it manually and deploy it onto your android device (not available for iOS).

## Instructions:
To do this, you will need Virtualbox, an android device, and some patience.

1. Go to this site: https://kivy.org/#download and download the Buildozer virtual machine (scroll down to the bottom and it is in the "Vitual Machine (for Android/buildozer)" section).

2. Extract the zip, and click on the "Buildozer VM.ovf" file, and open it with virtualbox.

3. Follow the steps on Virtualbox.

4. Start the VM. Once in the login screen, the password is "kivy".

5. Copy the KivyPad folder from the source code of this project onto the VM somehow (either using shared folders, clipboard or drag and drop settings in Virtualbox).

6. Open the terminal and navigate to where the KivyPad folder is.

7. Make sure the buildozer.spec file is in that folder. If it isn't, download it.

8. Plug your device into your computer.

9. Go to Devices --> USB at the top of the virtualbox window, and click your device on the list.

10. You will probably have to tap allow on your device, so make sure you have your device unlocked ready.

11. Once you can navigate to the device in the file manager of the VM, run the following command in the terminal we opened earlier:

```bash
buildozer android debug deploy
```
and wait.
"android" is the target, "debug" will build the code into an android package, and "deploy" will install it on your device.

12. Once this has finished, the app should be installed on your device. You can now shutdown the VM and unplug your device.

13. You will find the app in your applications menu on your device, as a home screen shortcut is not automatically made.

14. If you are having issues, you can debug the program by running:
```bash
buildozer android debug deploy run && buildozer android logcat | grep "python"
```
in the KivyPad folder while in the Kivy VM.

# NEA
This project is for you to complete your project.

# Deadline
You're expected to complete the code by the end of the summer holidays. The submission is after the first half term break in year 13.

# Documentation
Use the wiki for documentation and notes.
