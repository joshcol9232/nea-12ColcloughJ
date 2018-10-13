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

# NEA
This project is for you to complete your project.

# Deadline
You're expected to complete the code by the end of the summer holidays. The submission is after the first half term break in year 13.

# Documentation
Use the wiki for documentation and notes.
