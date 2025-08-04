import sys, shutil, os, requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer, Qt
from PyQt5.QtGui import QIcon

os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = "--disk-cache-size=1073741824 --disable-features=NetworkServiceInProcess --enable-features=NetworkService,CacheStorage,WebGLImageChromium --host-rules=*99"

shutil.rmtree(os.path.join(os.path.dirname(__file__),"offline_data"), ignore_errors=True)
app = QApplication(sys.argv)

ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

mainWindow = QWidget()
mainWindow.setFixedSize(1000, 200)
mainWindow.setWindowTitle("PenguinMod Downloader")
mainWindow.setWindowIcon(QIcon(ICON_PATH))

mainLayout = QVBoxLayout(mainWindow)
mainLayout.setContentsMargins(0, 0, 0, 0)

view = QWebEngineView()
profile = view.page().profile()
cache_path = os.path.join(os.path.dirname(__file__),"offline_data")
profile.setCachePath(cache_path)
profile.setHttpCacheType(profile.DiskHttpCache)
mainLayout.addWidget(view)

loader = QWidget(mainWindow)
loader.setStyleSheet("background-color: white;")

loaderLayout = QVBoxLayout(loader)
loaderLayout.setAlignment(Qt.AlignCenter)
loaderLayout.setContentsMargins(50, 0, 50, 0)

label = QLabel("Initializing...")
label.setStyleSheet("color: black; font-size: 24px;")
loaderLayout.addWidget(label)

progressBar_current = QProgressBar()
progressBar_current.setRange(0, 100)
progressBar_current.setValue(0)
progressBar_current.setStyleSheet("""
    QProgressBar {
        border: 2px solid grey;
        border-radius: 5px;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #05B8CC;
    }
""")
progressBar_current.setTextVisible(False)
loaderLayout.addWidget(progressBar_current)

progressBar_total = QProgressBar()
progressBar_total.setRange(0, 100)
progressBar_total.setValue(0)
progressBar_total.setStyleSheet("""
    QProgressBar {
        border: 2px solid grey;
        border-radius: 5px;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #05B8CC;
    }
""")
progressBar_total.setTextVisible(False)
loaderLayout.addWidget(progressBar_total)

class Downloader:
    def __init__(self, view, label, progress_bar_current, progress_bar_total, app_instance):
        self.view = view
        self.label = label
        self.progress_bar_current = progress_bar_current
        self.progress_bar_total = progress_bar_total
        self.app = app_instance
        self.files_to_download = []
        self.current_file_index = -1
        self.total_files = 0
        
        self.timeout_timer = QTimer()
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.handle_timeout)
        
        self.view.loadFinished.connect(self.on_load_finished)
        self.view.loadProgress.connect(self.update_current_progress)

    def start(self):
        self.label.setText("Fetching file list...")
        try:
            url = "https://raw.githubusercontent.com/pooiod/DesktopPenguinmod/refs/heads/main/files.json"
            response = requests.get(url)
            response.raise_for_status()
            
            all_files = response.json()
            html_files = [f for f in all_files if f.endswith(".html")]
            other_files = [f for f in all_files if not f.endswith(".html")]
            self.files_to_download = other_files + html_files
            
            self.total_files = len(self.files_to_download)
            if self.total_files > 0:
                self.progress_bar_total.setRange(0, self.total_files)
                self.load_next_file()
            else:
                self.label.setText("No files to download.")
                self.finish()
        except requests.exceptions.RequestException as e:
            self.label.setText("Error: Could not fetch file list.")
            QTimer.singleShot(3000, self.app.quit)

    def handle_timeout(self):
        self.view.stop()

    def update_current_progress(self, progress):
        self.progress_bar_current.setValue(progress)

    def load_next_file(self):
        self.current_file_index += 1
        if self.current_file_index < self.total_files:
            url = self.files_to_download[self.current_file_index]
            file_name = url.split('/')[-1]
            
            self.label.setText(f"Downloading: {file_name} ({self.current_file_index + 1}/{self.total_files})")
            self.progress_bar_current.setRange(0, 100)
            self.progress_bar_current.setValue(0)
            
            self.timeout_timer.start(6000)
            self.view.load(QUrl(url))
        else:
            self.finish()

    def on_load_finished(self, ok):
        self.timeout_timer.stop()
        
        self.progress_bar_total.setValue(self.current_file_index + 1)
        
        if not ok:
            current_url = self.view.url().toString()

        current_url_from_list = self.files_to_download[self.current_file_index]
        if current_url_from_list.endswith(".html"):
            QTimer.singleShot(5000, self.load_next_file)
        else:
            QTimer.singleShot(0, self.load_next_file)

    def finish(self):
        self.label.setText("Download Complete!")
        self.progress_bar_current.setValue(100)
        self.progress_bar_total.setValue(self.total_files)
        # QTimer.singleShot(1500, self.app.quit)
        QTimer.singleShot(1500, mainWindow.close)

mainWindow.show()
loader.setGeometry(0, 0, mainWindow.width(), mainWindow.height())
loader.raise_()

downloader = Downloader(view, label, progressBar_current, progressBar_total, app)
downloader.start()

sys.exit(app.exec_())
