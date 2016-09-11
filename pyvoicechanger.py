#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""PyVoiceChanger."""


import sys
from datetime import datetime
from subprocess import call
from time import sleep

from PyQt5.QtCore import QProcess, Qt, QTimer
from PyQt5.QtGui import QColor, QCursor, QIcon
from PyQt5.QtWidgets import (QApplication, QDial, QGraphicsDropShadowEffect,
                             QGroupBox, QLabel, QMainWindow, QMenu,
                             QShortcut, QSystemTrayIcon, QVBoxLayout)

from anglerfish import (check_encoding, make_logger, make_post_exec_msg,
                        set_process_name, set_single_instance,
                        set_desktop_launcher)


__version__ = '1.0.0'
__license__ = ' GPLv3+ LGPLv3+ '
__author__ = ' juancarlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/juancarlospaco/pyvoicechanger#pyvoicechanger'
start_time = datetime.now()
desktop_file_content = """
[Desktop Entry]
Comment=Voice Changer App.
Exec=chrt --idle 0 pyvoicechanger.py
GenericName=Voice Changer App.
Icon=audio-input-microphone
Name=PyVoiceChanger
StartupNotify=true
Terminal=false
Type=Application
Categories=Utility
X-DBUS-ServiceName=pyvoicechanger
X-KDE-StartupNotify=true
"""


###############################################################################


class MainWindow(QMainWindow):

    """Voice Changer main window."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.statusBar().showMessage("Move Dial to Deform Microphone Voice !.")
        self.setWindowTitle(__doc__)
        self.setMinimumSize(240, 240)
        self.setMaximumSize(480, 480)
        self.resize(self.minimumSize())
        self.setWindowIcon(QIcon.fromTheme("audio-input-microphone"))
        self.tray = QSystemTrayIcon(self)
        self.center()
        QShortcut("Ctrl+q", self, activated=lambda: self.close())
        self.menuBar().addMenu("&File").addAction("Quit", lambda: exit())
        self.menuBar().addMenu("Sound").addAction(
            "STOP !", lambda: call('killall rec', shell=True))
        windowMenu = self.menuBar().addMenu("&Window")
        windowMenu.addAction("Hide", lambda: self.hide())
        windowMenu.addAction("Minimize", lambda: self.showMinimized())
        windowMenu.addAction("Maximize", lambda: self.showMaximized())
        windowMenu.addAction("Restore", lambda: self.showNormal())
        windowMenu.addAction("FullScreen", lambda: self.showFullScreen())
        windowMenu.addAction("Center", lambda: self.center())
        windowMenu.addAction("Top-Left", lambda: self.move(0, 0))
        windowMenu.addAction("To Mouse", lambda: self.move_to_mouse_position())
        # widgets
        group0 = QGroupBox("Voice Deformation")
        self.setCentralWidget(group0)
        self.process = QProcess(self)
        self.process.error.connect(
            lambda: self.statusBar().showMessage("Info: Process Killed", 5000))
        self.control = QDial()
        self.control.setRange(-10, 20)
        self.control.setSingleStep(5)
        self.control.setValue(0)
        self.control.setCursor(QCursor(Qt.OpenHandCursor))
        self.control.sliderPressed.connect(
            lambda: self.control.setCursor(QCursor(Qt.ClosedHandCursor)))
        self.control.sliderReleased.connect(
            lambda: self.control.setCursor(QCursor(Qt.OpenHandCursor)))
        self.control.valueChanged.connect(
            lambda: self.control.setToolTip("<b>" + str(self.control.value())))
        self.control.valueChanged.connect(
            lambda: self.statusBar().showMessage(
                "Voice deformation: " + str(self.control.value()), 5000))
        self.control.valueChanged.connect(self.run)
        self.control.valueChanged.connect(lambda: self.process.kill())
        # Graphic effect
        self.glow = QGraphicsDropShadowEffect(self)
        self.glow.setOffset(0)
        self.glow.setBlurRadius(99)
        self.glow.setColor(QColor(99, 255, 255))
        self.control.setGraphicsEffect(self.glow)
        self.glow.setEnabled(False)
        # Timer to start
        self.slider_timer = QTimer(self)
        self.slider_timer.setSingleShot(True)
        self.slider_timer.timeout.connect(self.on_slider_timer_timeout)
        # an icon and set focus
        QLabel(self.control).setPixmap(
            QIcon.fromTheme("audio-input-microphone").pixmap(32))
        self.control.setFocus()
        QVBoxLayout(group0).addWidget(self.control)
        self.menu = QMenu(__doc__)
        self.menu.addAction(__doc__).setDisabled(True)
        self.menu.setIcon(self.windowIcon())
        self.menu.addSeparator()
        self.menu.addAction(
            "Show / Hide",
            lambda: self.hide() if self.isVisible() else self.showNormal())
        self.menu.addAction("STOP !", lambda: call('killall rec', shell=True))
        self.menu.addSeparator()
        self.menu.addAction("Quit", lambda: exit())
        self.tray.setContextMenu(self.menu)
        self.make_trayicon()

    def run(self):
        """Run/Stop the QTimer."""
        if self.slider_timer.isActive():
            self.slider_timer.stop()
        self.glow.setEnabled(True)
        call('killall rec', shell=True)
        self.slider_timer.start(3000)

    def on_slider_timer_timeout(self):
        """Run subprocess to deform voice."""
        self.glow.setEnabled(False)
        value = int(self.control.value()) * 100
        cmd = 'play -q -V0 "|rec -q -V0 -n -d -R riaa bend pitch {0} "'
        command = cmd.format(int(value))
        log.debug("Voice Deformation Value: {0}".format(value))
        log.debug("Voice Deformation Command: {0}".format(command))
        self.process.start(command)
        if self.isVisible():
            self.statusBar().showMessage("Minimizing to System TrayIcon", 3000)
            log.debug("Minimizing Main Window to System TrayIcon now...")
            sleep(3)
            self.hide()

    def center(self):
        """Center Window on the Current Screen,with Multi-Monitor support."""
        window_geometry = self.frameGeometry()
        mousepointer_position = QApplication.desktop().cursor().pos()
        screen = QApplication.desktop().screenNumber(mousepointer_position)
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        window_geometry.moveCenter(centerPoint)
        self.move(window_geometry.topLeft())

    def move_to_mouse_position(self):
        """Center the Window on the Current Mouse position."""
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(QApplication.desktop().cursor().pos())
        self.move(window_geometry.topLeft())

    def make_trayicon(self):
        """Make a Tray Icon."""
        if self.windowIcon() and __doc__:
            self.tray.setIcon(self.windowIcon())
            self.tray.setToolTip(__doc__)
            self.tray.activated.connect(
                lambda: self.hide() if self.isVisible()
                else self.showNormal())
            return self.tray.show()


###############################################################################


def main():
    """Main Loop."""
    global log
    log = make_logger("pyvoicechanger")
    log.debug(__doc__ + __version__ + __url__)
    check_encoding()
    set_process_name("pyvoicechanger")
    set_single_instance("pyvoicechanger")
    set_desktop_launcher("pyvoicechanger", desktop_file_content)
    application = QApplication(sys.argv)
    application.setApplicationName("pyvoicechanger")
    application.setOrganizationName("pyvoicechanger")
    application.setOrganizationDomain("pyvoicechanger")
    application.setWindowIcon(QIcon.fromTheme("audio-input-microphone"))
    application.aboutToQuit.connect(lambda: call('killall rec', shell=True))
    mainwindow = MainWindow()
    mainwindow.show()
    make_post_exec_msg(start_time)
    sys.exit(application.exec_())


if __name__ in '__main__':
    main()
