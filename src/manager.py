import sys, shutil, os, requests, json, socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar, QListWidget, QLineEdit, QHBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, QTimer, QProcess, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

DOMAINS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domains.json")
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_data")
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

def RunProgram(file):
    import os, sys
    import PyQt5.QtWidgets as qw
    def fake_exit(code=0):
        raise SystemExit(code)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    code = open(path).read()
    real = qw.QApplication
    inst = real.instance()
    class Q(real):
        def __new__(cls, *a, **k):
            if inst:
                return inst
            return real.__new__(real, *a, **k)
    qw.QApplication = Q
    old_exit = sys.exit
    sys.exit = fake_exit
    try:
        exec(code, globals())
    except SystemExit:
        pass
    finally:
        sys.exit = old_exit
        qw.QApplication = real

class WhitelistEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Penguin Memory Manager")
        self.setMinimumSize(500, 300)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.list = QListWidget()
        self.input = QLineEdit()
        self.btn_add = QPushButton("Add")
        self.btn_remove = QPushButton("Remove")
        self.lbl_cache = QLabel()
        if self.cache_size_mb() == 0:
            self.btn_reinstall = QPushButton("Install PenguinMod")
        else:
            self.btn_reinstall = QPushButton("Re-install PenguinMod")
        self.layout = QVBoxLayout()
        self.label = QLabel("Offline domains")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list)
        h = QHBoxLayout()
        h.addWidget(self.input)
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_remove)
        self.layout.addLayout(h)
        self.layout.addWidget(self.lbl_cache)
        self.layout.addWidget(self.btn_reinstall)
        self.setLayout(self.layout)
        self.btn_add.clicked.connect(self.add_domain)
        self.btn_remove.clicked.connect(self.remove_domain)
        self.btn_reinstall.clicked.connect(self.reinstall)
        self.proc = QProcess(self)
        self.proc.finished.connect(self.on_finished)
        self.load_domains()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)
        self.update_status()

    def load_domains(self):
        with open(DOMAINS_PATH,"r") as f:
            self.domains = json.load(f)
        self.list.clear()
        self.list.addItems(self.domains)

    def save_domains(self):
        with open(DOMAINS_PATH,"w") as f:
            json.dump(self.domains,f,indent=2)

    def add_domain(self):
        d = self.input.text().strip()
        if d and d not in self.domains:
            self.domains.append(d)
            self.save_domains()
            self.load_domains()
            self.input.clear()

    def remove_domain(self):
        for i in self.list.selectedItems():
            d = i.text()
            if d in self.domains:
                self.domains.remove(d)
        self.save_domains()
        self.load_domains()

    def cache_size_mb(self):
        total=0
        for root,_,files in os.walk(CACHE_PATH):
            for f in files:
                total+=os.path.getsize(os.path.join(root,f))
        return total/1024/1024

    def is_online(self):
        try:
            socket.create_connection(("8.8.8.8",53),2).close()
            return True
        except:
            return False

    def update_status(self):
        self.lbl_cache.setText(f"Cache size: {self.cache_size_mb():.2f} MB")
        self.btn_reinstall.setEnabled(self.is_online())

    def reinstall(self):
        self.btn_reinstall.setEnabled(False)
        self.btn_reinstall.setText("Installing...")
        RunProgram('install.py')

    def on_finished(self):
        self.btn_reinstall.setText("Re-install PenguinMod")
        QMessageBox.information(self, "Reinstall", "PenguinMod has been reinstalled successfully.")
        self.btn_reinstall.setEnabled(self.is_online())

if __name__=="__main__":
    app=QApplication(sys.argv)
    w=WhitelistEditor()
    w.show()
    sys.exit(app.exec_())
