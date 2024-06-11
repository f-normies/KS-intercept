import sys
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, QThread, Signal)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QMainWindow, QMenu,
    QMenuBar, QPushButton, QScrollArea, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget, QLabel, QDialog, QMessageBox)

import subprocess
from pathlib import Path
import logging

import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

import platform

from src.gui.mainwindow_base import Ui_MainWindow
from src.gui.settings_base import Ui_Dialog

class FileWatcherHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.src_path.endswith('intercepted_data.json'):
            self.callback()

    def on_created(self, event):
        if event.src_path.endswith('intercepted_data.json'):
            self.callback()

class FileWatcherThread(QThread):
    update_signal = Signal(list)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.timestamps = set()
        self.observer = Observer()
        self.event_handler = FileWatcherHandler(self.process_file)
        self.observer.schedule(self.event_handler, self.directory, recursive=False)

    def run(self):
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            self.observer.stop()
            self.observer.join()

    def process_file(self):
        file_path = Path(self.directory) / 'intercepted_data.json'
        if not file_path.exists():
            return

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                data = json.load(file)

            new_timestamps = {entry['timestamp'] for entry in data if 'timestamp' in entry}
            self.timestamps.update(new_timestamps)
            sorted_timestamps = sorted(self.timestamps)
            self.update_signal.emit(sorted_timestamps)

        except Exception as e:
            logging.error(f"Error processing file: {e}")

class SettingsDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)

        self.saveButton.clicked.connect(self.save_settings)
        self.configureButton.clicked.connect(self.install_dependencies)
    
    def show_message(self, title, message, icon):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(icon)
            msg_box.exec()

    def save_settings(self):
        # ...
        self.accept()
    
    def install_dependencies(self):
        subprocess.run(["pip", "install", "-r", "requirements.txt"], capture_output=True, text=True)
        
        os_name = platform.system()

        if os_name == "Windows":
            subprocess.run(["cd", "%USERPROFILE%/.mitmproxy"], capture_output=True, text=True)
            subprocess.run(["certutil", "-addstore", "-f", "\"ROOT\"", "mitmproxy-ca-cert.pem"], capture_output=True, text=True)
        elif os_name == "Darwin":  # macOS
            subprocess.run(["cd", "~/.mitmproxy"], capture_output=True, text=True)
            subprocess.run(["sudo", "security", "add-trusted-cert", "-d", "-r", "trustRoot", "-k", "/Library/Keychains/System.keychain mitmproxy-ca-cert.pem"], capture_output=True, text=True)
        elif os_name == "Linux":
            self.show_message("Сертификаты MITMProxy", "Вы используете Linux. Пожалуйста, установите CA сертификаты (~/.mitmproxy) самостоятельно, подходящим для вашего дистрибутива образом.", QMessageBox.Information)
        else:
            print(f"Unsupported OS: {os_name}")
            return
            
        # Close the dialog
        self.accept()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.script_running = False

        self.script_path = Path(__file__).resolve().parent.parent / "intercept"

        self.proxyButton.clicked.connect(self.toggle_script)
        self.saveButton.clicked.connect(self.save_intercepted_data)

        self.scroll_layout = QVBoxLayout(self.scrollAreaWidgetContents_2)
        
        self.file_watcher_thread = FileWatcherThread(self.script_path)
        self.file_watcher_thread.update_signal.connect(self.update_scroll_area)
        self.file_watcher_thread.start()

        self.actionSettings = QAction("&Настройки", self)
        self.menuSettings.addAction(self.actionSettings)
        self.actionSettings.triggered.connect(self.open_settings_dialog)

    def toggle_script(self):
        if self.script_running:
            self.stop_script()
        else:
            self.start_script()

    def start_script(self):
        logging.info('Starting script...')
        self.process = subprocess.Popen(["python", "cli.py", "start"], cwd=self.script_path)
        self.proxyButton.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c", None))
        self.script_running = True
        logging.info('Script started')

    def stop_script(self):
        logging.info('Stopping script...')
        subprocess.run(["python", "cli.py", "stop"], cwd=self.script_path)
        self.proxyButton.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0440\u0442", None))
        self.script_running = False
        logging.info('Script stopped')
    
    def save_intercepted_data(self):
        logging.info('Saving intercepted data...')
        subprocess.run(["python", "cli.py", "save"], cwd=self.script_path)
        logging.info('Intercepted data saved')
        
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def update_scroll_area(self, timestamps):
        # Clear existing labels
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add new labels with timestamps
        for index, timestamp in enumerate(timestamps):
            label = QLabel(f"{index + 1} - {timestamp}")
            self.scroll_layout.addWidget(label)
    
    def closeEvent(self, event):
        logging.info('Application is closing...')
        if self.script_running:
            self.stop_script()
        event.accept()

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())