#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP8:OK, LINT:OK, PY3:OK


# metadata
"""PyVoiceChanger."""
__package__ = "pyvoicechanger"
__version__ = ' 0.0.1 '
__license__ = ' GPLv3+ LGPLv3+ '
__author__ = ' juancarlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/juancarlospaco/pyvoicechanger#pyvoicechanger'
__source__ = ('https://raw.githubusercontent.com/juancarlospaco/'
              'pyvoicechanger/master/pyvoicechanger.py')


# imports
import os
import sys
from ctypes import byref, cdll, create_string_buffer
from getopt import getopt
import logging as log
from copy import copy
from subprocess import call
from urllib import request
from webbrowser import open_new_tab

from PyQt5.QtCore import QProcess, Qt, QTimer
from PyQt5.QtGui import QColor, QCursor, QIcon
from PyQt5.QtWidgets import (QApplication, QDial, QFontDialog,
                             QGraphicsDropShadowEffect, QGroupBox, QLabel,
                             QMainWindow, QMessageBox, QShortcut, QVBoxLayout)


HELP = """<h3>PyVoiceChanger</h3><b>Microphone Voice Deformation App !.</b><br>
Version {}, licence {}. DEV: <a href=https://github.com/juancarlospaco>Juan</a>
<br>QA: <a href=https://github.com/rokarc>rokarc</a>
""".format(__version__, __license__)


###############################################################################


class MainWindow(QMainWindow):

    """Voice Changer main window."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.statusBar().showMessage("Move the Dial to Deform mic voice !")
        self.setWindowTitle(__doc__.strip().capitalize())
        self.setMinimumSize(240, 240)
        self.setMaximumSize(480, 480)
        self.resize(self.minimumSize())
        self.setWindowIcon(QIcon.fromTheme("audio-input-microphone"))
        self.center()
        QShortcut("Ctrl+q", self, activated=lambda: self.close())
        self.menuBar().addMenu("&File").addAction("Exit", self.close)
        windowMenu = self.menuBar().addMenu("&Window")
        windowMenu.addAction("Minimize", lambda: self.showMinimized())
        windowMenu.addAction("Maximize", lambda: self.showMaximized())
        windowMenu.addAction("Restore", lambda: self.showNormal())
        windowMenu.addAction("FullScreen", lambda: self.showFullScreen())
        windowMenu.addAction("Center", lambda: self.center())
        windowMenu.addAction("Top-Left", lambda: self.move(0, 0))
        windowMenu.addAction("To Mouse", lambda: self.move_to_mouse_position())
        windowMenu.addSeparator()
        windowMenu.addAction(
            "Increase size", lambda:
            self.resize(self.size().width() * 1.4, self.size().height() * 1.4))
        windowMenu.addAction("Decrease size", lambda: self.resize(
            self.size().width() // 1.4, self.size().height() // 1.4))
        windowMenu.addAction("Minimum size", lambda:
                             self.resize(self.minimumSize()))
        windowMenu.addAction("Maximum size", lambda:
                             self.resize(self.maximumSize()))
        windowMenu.addAction("Horizontal Wide", lambda: self.resize(
            self.maximumSize().width(), self.minimumSize().height()))
        windowMenu.addAction("Vertical Tall", lambda: self.resize(
            self.minimumSize().width(), self.maximumSize().height()))
        windowMenu.addSeparator()
        windowMenu.addAction("Disable Resize", lambda:
                             self.setFixedSize(self.size()))
        windowMenu.addAction("Set Interface Font...", lambda:
                             self.setFont(QFontDialog.getFont()[0]))
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("About Qt 5", lambda: QMessageBox.aboutQt(self))
        helpMenu.addAction("About Python 3",
                           lambda: open_new_tab('https://www.python.org'))
        helpMenu.addAction("About" + __doc__,
                           lambda: QMessageBox.about(self, __doc__, HELP))
        helpMenu.addSeparator()
        helpMenu.addAction(
            "Keyboard Shortcut",
            lambda: QMessageBox.information(self, __doc__, "Quit = CTRL+Q"))
        helpMenu.addAction("View Source Code",
                           lambda: call('xdg-open ' + __file__, shell=True))
        helpMenu.addAction("View GitHub Repo", lambda: open_new_tab(__url__))
        helpMenu.addAction("Report Bugs", lambda: open_new_tab(
            'https://github.com/juancarlospaco/pyvoicechanger/issues'))
        helpMenu.addAction("Check Updates", lambda: self.check_for_updates())
        # widgets
        group0 = QGroupBox("Voice Deformation")
        self.setCentralWidget(group0)
        self.process = QProcess(self)
        self.process.error.connect(
            lambda: self.statusBar().showMessage("Info: Process Killed", 5000))
        # self.process3.finished.connect(self.on_process3_finished)
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
        self.process.start(
            'play -q -V0 "|rec -q -V0 -n -d -R riaa pitch {} "'.format(value)
            if value != 0
            else 'play -q -V0 "|rec -q -V0 --multi-threaded -n -d -R bend {} "'
            .format(' 3,2500,3 3,-2500,3 ' * 999))

    def check_for_updates(self):
        """Method to check for updates from Git repo versus this version."""
        this_version = str(open(__file__).read())
        last_version = str(request.urlopen(__source__).read().decode("utf8"))
        if this_version != last_version:
            m = "Theres new Version available!<br>Download update from the web"
        else:
            m = "No new updates!<br>You have the lastest version of this app"
        return QMessageBox.information(self, __doc__.title(), "<b>" + m)

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

    def closeEvent(self, event):
        """Ask to Quit."""
        the_conditional_is_true = QMessageBox.question(
            self, __doc__.title(), 'Quit ?.', QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No) == QMessageBox.Yes
        event.accept() if the_conditional_is_true else event.ignore()


###############################################################################


def main():
    """Main Loop."""
    APPNAME = str(__package__ or __doc__)[:99].lower().strip().replace(" ", "")
    if not sys.platform.startswith("win") and sys.stderr.isatty():
        def add_color_emit_ansi(fn):
            """Add methods we need to the class."""
            def new(*args):
                """Method overload."""
                if len(args) == 2:
                    new_args = (args[0], copy(args[1]))
                else:
                    new_args = (args[0], copy(args[1]), args[2:])
                if hasattr(args[0], 'baseFilename'):
                    return fn(*args)
                levelno = new_args[1].levelno
                if levelno >= 50:
                    color = '\x1b[31m'  # red
                elif levelno >= 40:
                    color = '\x1b[31m'  # red
                elif levelno >= 30:
                    color = '\x1b[33m'  # yellow
                elif levelno >= 20:
                    color = '\x1b[32m'  # green
                elif levelno >= 10:
                    color = '\x1b[35m'  # pink
                else:
                    color = '\x1b[0m'  # normal
                try:
                    new_args[1].msg = color + str(new_args[1].msg) + '\x1b[0m'
                except Exception as reason:
                    print(reason)  # Do not use log here.
                return fn(*new_args)
            return new
        # all non-Windows platforms support ANSI Colors so we use them
        log.StreamHandler.emit = add_color_emit_ansi(log.StreamHandler.emit)
    log.basicConfig(level=-1, format="%(levelname)s:%(asctime)s %(message)s")
    log.getLogger().addHandler(log.StreamHandler(sys.stderr))
    try:
        os.nice(19)  # smooth cpu priority
        libc = cdll.LoadLibrary('libc.so.6')  # set process name
        buff = create_string_buffer(len(APPNAME) + 1)
        buff.value = bytes(APPNAME.encode("utf-8"))
        libc.prctl(15, byref(buff), 0, 0, 0)
    except Exception as reason:
        log.warning(reason)
    application = QApplication(sys.argv)
    application.setApplicationName(__doc__.strip().lower())
    application.setOrganizationName(__doc__.strip().lower())
    application.setOrganizationDomain(__doc__.strip())
    application.setWindowIcon(QIcon.fromTheme("audio-input-microphone"))
    application.aboutToQuit.connect(lambda: call('killall rec', shell=True))
    try:
        opts, args = getopt(sys.argv[1:], 'hv', ('version', 'help'))
    except:
        pass
    for o, v in opts:
        if o in ('-h', '--help'):
            print(APPNAME + ''' Usage:
                  -h, --help        Show help informations and exit.
                  -v, --version     Show version information and exit.''')
            return sys.exit(0)
        elif o in ('-v', '--version'):
            print(__version__)
            return sys.exit(0)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(application.exec_())


if __name__ in '__main__':
    main()
