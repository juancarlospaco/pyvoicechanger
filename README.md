pyvoicechanger
==============

- Real Time Microphone Voice Changer App. Works with On-Line Games and VideoConferences!

![screenshot](https://source.unsplash.com/DoA2duXyzRM/800x400 "Illustrative Photo by https://unsplash.com/@clemono2")

![screenshot](https://raw.githubusercontent.com/juancarlospaco/pyvoicechanger/master/temp.jpg)
![screenshot](https://raw.githubusercontent.com/juancarlospaco/pyvoicechanger/master/temp2.jpg)


# Install

Debian/Ubuntu: `sudo apt-get install sox python3-pyqt5`

Centos/RedHat: `sudo yum install python3-qt5 sox`

Arch: `sudo pacman -S python-pyqt5 sox`

```
sudo pip install pyvoicechanger
```

**Run:** `pyvoicechanger.py`


# Requisites

- [Python 3.6+](https://www.python.org "Python Homepage")
- [PyQt 5.10+](http://www.riverbankcomputing.co.uk/software/pyqt/download5 "PyQt5 Homepage")
- Sox *(Linux package)*.
- Working Microphone, Speakers and Sound System.
- Working Sound Loopback Kernel Module


# Troubleshooting

<details>
<summary>If its not working</summary>

`modprobe snd-aloop`

This command MUST be successful, Sound Loopback Kernel Module MUST be up & running,
if it fails you dont have Sound Loopback Kernel Module up & running,
if it says `modprobe: FATAL: Module aloop not found ...` it failed,
please check your Distro Documentation about Sound Loopback Kernel Module to fix it,
sometimes you need to enable it, or recompile it, or reinstall it, or whatever
(that is not my Bug, complain to your Distro).

Check your Python version executing `python --version`, it should say `3.6.0` or higher.

</details>
