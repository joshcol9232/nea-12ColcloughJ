# Dependencies:
- Python 3
- Kivy (install via pip):
  - Cython
  - sdl2/pygame (either is fine)
- PyBluez (install via pip):
  - Bluez devel package on linux

# Install on Linux
## Follow install process for kivy:
https://kivy.org/doc/stable/installation/installation-linux.html

## All Distro's:
```
pip3 install cython kivy pygame pybluez
```
You might need some linux headers for PyBluez:
### Arch based:
```
uname -r
```
To get kernel version, then:
```
sudo pacman -S linux-headers bluez-libs
```
Then select appropriate headers for your kernel.
### Debian based:
```
uname -r
```
To get kernel version, then:
```
sudo apt install linux-headers bluez libbluetooth-dev
```
Then select appropriate headers for your kernel.

# Run program:
Change directory to where you installed it, then cd to "code".
Then execute:
```
python3 start.py
```
If it crashes make sure your config file is configured correctly.

# NEA
This project is for you to complete your project.

# Deadline
You're expected to complete the code by the end of the summer holidays. The submission is after the first half term break in year 13.

# Documentation
Use the wiki for documentation and notes.
