import sys, shutil, os, requests, json, socket, time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar, QListWidget, QLineEdit, QHBoxLayout, QLabel, QMainWindow, QShortcut, QMessageBox, QInputDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineScript, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineHttpRequest
from PyQt5.QtCore import QUrl, QTimer, QProcess, Qt
from PyQt5.QtGui import QIcon, QKeySequence

# some things will not load if I enable web security
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-web-security --allow-running-insecure-content --disable-site-isolation-trials --disable-features=CrossOriginOpenerPolicy,CrossOriginEmbedderPolicy --user-data-dir=/tmp/pm_chromium"

DOMAINS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domains.json")
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_data")
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

# this function was anoying to figure out
def RunProgram(file):
    def fake_exit(code=0):
        raise SystemExit(code)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    with open(path) as f:
        old_exit = sys.exit
        sys.exit = fake_exit
        try:
            exec(f.read(), globals())
        except SystemExit:
            pass
        finally:
            sys.exit = old_exit

# the installer is build into the program
if not os.path.exists(CACHE_PATH):
    RunProgram('install.py')

with open(DOMAINS_PATH, "r") as f:
    WHITELIST = json.load(f)

class WebPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self._session_permissions = {}
        self.featurePermissionRequested.connect(self.on_feature_permission_requested)
        self.windowCloseRequested.connect(self.window_close_requested)
        self.loadFinished.connect(self.on_load_finished)

    def on_feature_permission_requested(self, url, feature):
        origin_str = f"{url.scheme()}://{url.host()}"
        if url.port() != -1:
            origin_str += f":{url.port()}"
        permission_key = (origin_str, feature)
        if permission_key in self._session_permissions:
            self.setFeaturePermission(url, feature, self._session_permissions[permission_key])
            return
        feature_map = {
            QWebEnginePage.MediaAudioCapture: "use your microphone",
            QWebEnginePage.MediaVideoCapture: "use your camera",
            QWebEnginePage.Geolocation: "access your location",
            QWebEnginePage.Notifications: "show notifications",
            QWebEnginePage.MediaAudioVideoCapture: "capture audio and video",
            QWebEnginePage.DesktopVideoCapture: "capture your screen",
            QWebEnginePage.DesktopAudioVideoCapture: "capture your screen and audio",
            QWebEnginePage.MouseLock: "lock your mouse cursor",
        }
        question = f"Do you want to allow this project to {feature_map.get(feature, 'use this feature')}?"
        msg = QMessageBox(self.view().window())
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Permission")
        msg.setText(question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        permission = QWebEnginePage.PermissionGrantedByUser if msg.exec_() == QMessageBox.Yes else QWebEnginePage.PermissionDeniedByUser
        self.setFeaturePermission(url, feature, permission)
        self._session_permissions[permission_key] = permission

    def on_load_finished(self, ok):
        self._session_permissions.clear()

    def window_close_requested(self):
        self.parent().close()

    def javaScriptAlert(self, securityOrigin, msg):
        mb = QMessageBox(self.view().window())
        mb.setIcon(QMessageBox.Information)
        mb.setWindowTitle("Alert")
        mb.setText(msg)
        mb.exec_()

    def javaScriptConfirm(self, securityOrigin, msg):
        mb = QMessageBox(self.view().window())
        mb.setIcon(QMessageBox.Question)
        mb.setWindowTitle("Confirm")
        mb.setText(msg)
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return mb.exec_() == QMessageBox.Yes

    def javaScriptPrompt(self, securityOrigin, msg, default):
        text, ok = QInputDialog.getText(self.view().window(), "Prompt", msg, text=default)
        return text if ok else ""

class OfflineInterceptor(QWebEngineUrlRequestInterceptor):
    # any domain in the whiteist will be stored for offline use
    def interceptRequest(self, info):
        host = info.requestUrl().host()
        allowed = any(host == d or host.endswith("." + d) for d in WHITELIST)
        info.setHttpHeader(b"Cache-Control", b"max-age=3122064000" if allowed else b"no-store") # I don't think most people will be using this program for 99 years

def inject_script(profile):
    # polyfill script to add functions that Penguinmod needs to function
    # this is not directly in script.js because it counts as a browser fix
    polyfill = """
    if(!String.prototype.replaceAll){
        String.prototype.replaceAll=function(s,r){
            return this.split(s).join(r)
        }
    };
    if (!String.prototype.at) {
        String.prototype.at = function(n) {
            n = Math.trunc(n) || 0;
            if (n < 0) n += this.length;
            if (n < 0 || n >= this.length) return undefined;
            return this.charAt(n);
        };
    }

    if (!window.structuredClone) {
        window.structuredClone = function(obj) {
            return JSON.parse(JSON.stringify(obj));
        };
    }

    if (!Array.prototype.at) {
        Array.prototype.at = function(n) {
            n = Math.trunc(n) || 0;
            if (n < 0) n += this.length;
            if (n < 0 || n >= this.length) return undefined;
            return this[n];
        };
    }
    """
    # also add script.js because cool features
    path = os.path.join(os.path.dirname(__file__), "script.js")
    code = polyfill + open(path).read() if os.path.exists(path) else polyfill
    s = QWebEngineScript()
    s.setName("injected")
    s.setSourceCode(code)
    s.setInjectionPoint(QWebEngineScript.DocumentReady)
    s.setWorldId(QWebEngineScript.MainWorld)
    s.setRunsOnSubFrames(True)
    profile.scripts().insert(s)

class Browser(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last = None
        self._retry = False
        self.page().loadFinished.connect(self._on_load_finished)

    def load(self, url):
        self._last = QUrl(url) if isinstance(url, str) else url
        super().load(self._last)

    def _on_load_finished(self, ok):
        if not ok and not self._retry and self._last:
            self._retry = True
            req = QWebEngineHttpRequest(self._last)
            req.setHeader(b"Cache-Control", b"only-if-cached")
            self.page().load(req)
        else:
            self._retry = False

    def createWindow(self, _):
        win = Window(profile=self.page().profile(), parent=self.window())
        win.resize(1024, 768)
        win.setWindowTitle("External Content")
        windows.append(win)
        win.show()
        return win.view

    def contextMenuEvent(self, e):
        m = self.page().createStandardContextMenu()
        for a in (QWebEnginePage.SavePage, QWebEnginePage.ViewSource):
            act = self.page().action(a)
            if act:
                m.removeAction(act)
        m.exec_(e.globalPos())

class Window(QMainWindow):
    def __init__(self, profile, parent=None):
        super().__init__(parent)
        self.view = Browser()
        page = WebPage(profile, self)
        s = page.settings()
        s.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)
        s.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        s.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, False)
        s.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        s.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        s.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        s.setAttribute(QWebEngineSettings.JavascriptCanPaste, True)
        s.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.view.setPage(page)
        self.setCentralWidget(self.view)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setWindowTitle("PenguinMod Desktop")
        self.resize(1824, 968)
        self.setMinimumSize(1024, 768)
        if not parent:
            self.view.load("https://studio.penguinmod.com/editor.html")
            self.view.setZoomFactor(1.2)
        self.devtools = None
        QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(lambda: self.OpenManager())
        QShortcut(QKeySequence("Ctrl+Shift+I"), self).activated.connect(self.open_devtools)
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(lambda: self.view.setZoomFactor(self.view.zoomFactor()*1.1))
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(lambda: self.view.setZoomFactor(self.view.zoomFactor()*0.9))
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(lambda: self.view.setZoomFactor(1.0))

    def OpenManager(self):
        QTimer.singleShot(1000, main.close)
        RunProgram("manager.py")

    def open_devtools(self):
        if not self.devtools:
            self.devtools = QMainWindow(self)
            dv = QWebEngineView()
            dv.setZoomFactor(1.2)
            self.devtools.setCentralWidget(dv)
            self.devtools.resize(800,600)
            self.view.page().setDevToolsPage(dv.page())
            QShortcut(QKeySequence("Ctrl+="), self.devtools).activated.connect(lambda: dv.setZoomFactor(dv.zoomFactor()*1.1))
            QShortcut(QKeySequence("Ctrl+-"), self.devtools).activated.connect(lambda: dv.setZoomFactor(dv.zoomFactor()*0.9))
            QShortcut(QKeySequence("Ctrl+0"), self.devtools).activated.connect(lambda: dv.setZoomFactor(1.0))
        self.devtools.show()
        self.view.page().triggerAction(QWebEnginePage.InspectElement)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    profile = QWebEngineProfile("sharedProfile")
    profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.144 Safari/537.36")
    profile.setCachePath(CACHE_PATH)
    profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
    profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
    interceptor = OfflineInterceptor()
    profile.setUrlRequestInterceptor(interceptor)
    inject_script(profile)
    main = Window(profile=profile)
    windows = [main]
    main.show()
    sys.exit(app.exec_())
