#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PEP8:OK, LINT:OK, PY3:OK


# metadata
""" PyVoiceChanger """
__version__ = ' 0.0.1 '
__license__ = ' GPLv3+ '
__author__ = ' juancarlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/juancarlospaco/pyvoicechanger#pyvoicechanger'


# imports
import sys
from getopt import getopt
from subprocess import call
from webbrowser import open_new_tab

from PyQt5.QtCore import QTimer, Qt, QProcess
from PyQt5.QtGui import QColor, QIcon, QCursor
from PyQt5.QtWidgets import (QApplication, QDial, QGraphicsDropShadowEffect,
                             QGroupBox, QLabel, QMainWindow, QMessageBox,
                             QShortcut, QVBoxLayout)


HELP = """<h3>PyVoiceChanger</h3><b>Microphone Voice Deformation App !.</b><br>
Version {}, licence {}. DEV: <a href=https://github.com/juancarlospaco>Juan</a>
""".format(__version__, __license__)


###############################################################################


class MainWindow(QMainWindow):
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
        self.menuBar().addMenu("&File").addAction("Exit", exit)
        windowMenu = self.menuBar().addMenu("&Window")
        windowMenu.addAction("Minimize", lambda: self.showMinimized())
        windowMenu.addAction("Maximize", lambda: self.showMaximized())
        windowMenu.addAction("Restore", lambda: self.showNormal())
        windowMenu.addAction("Center", lambda: self.center())
        windowMenu.addAction("To Mouse", lambda: self.move_to_mouse_position())
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction("About Qt 5", lambda: QMessageBox.aboutQt(self))
        helpMenu.addAction("About Python 3",
                           lambda: open_new_tab('https://www.python.org'))
        helpMenu.addAction("About" + __doc__,
                           lambda: QMessageBox.about(self, __doc__, HELP))
        helpMenu.addSeparator()
        helpMenu.addAction("Keyboard Shortcut", lambda: QMessageBox.information(
            self, __doc__, "Quit = CTRL+Q"))
        helpMenu.addAction("View Source Code",
                           lambda: call('xdg-open ' + __file__, shell=True))
        helpMenu.addAction("View GitHub Repo", lambda: open_new_tab(__url__))
        # widgets
        group0 = QGroupBox("Voice Deformation")
        self.setCentralWidget(group0)
        self.process = QProcess(self)
        self.process.error.connect(
            lambda: self.statusBar().showMessage("Info: Process Killed!", 5000))
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

    def center(self):
        """Center the Window on the Current Screen,with Multi-Monitor support"""
        window_geometry = self.frameGeometry()
        mousepointer_position = QApplication.desktop().cursor().pos()
        screen = QApplication.desktop().screenNumber(mousepointer_position)
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        window_geometry.moveCenter(centerPoint)
        self.move(window_geometry.topLeft())

    def move_to_mouse_position(self):
        """Center the Window on the Current Mouse position"""
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(QApplication.desktop().cursor().pos())
        self.move(window_geometry.topLeft())

    def closeEvent(self, event):
        ' Ask to Quit '
        the_conditional_is_true = QMessageBox.question(
            self, __doc__.title(), 'Quit ?.', QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No) == QMessageBox.Yes
        event.accept() if the_conditional_is_true else event.ignore()


###############################################################################


def main():
    ' Main Loop '
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
            print(''' Usage:
                  -h, --help        Show help informations and exit.
                  -v, --version     Show version information and exit.''')
            return sys.exit(1)
        elif o in ('-v', '--version'):
            print(__version__)
            return sys.exit(1)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(application.exec_())


if __name__ in '__main__':
    main()
