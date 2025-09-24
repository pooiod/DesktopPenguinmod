# This is a test to see if it is possible to use microsoft WebView2 (via pywebview)
# and a proxy do do the things PyQt5 does, but on a modern browser
# also it makes the project smaller since webview2 is built into Windows

# I am new to pywebview so most of this is stack overflow code
# do NOT use this code yet, it is extreamly unfinished

import webview
import os
import json
import threading
import http.server
import socketserver
import requests
import urllib.parse
import mimetypes
import socket
import select

DOMAINS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domains.json")
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_data")
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8888
WHITELIST = []

# man in the middle ahh code
class CachingProxy(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        hostname, port_str = self.path.split(':', 1)
        port = int(port_str)
        print(f"[PROXY LOG] CONNECT request to {hostname}:{port}")

        try:
            dest_socket = socket.create_connection((hostname, port))
        except socket.error as e:
            print(f"[PROXY LOG] ERROR: Could not connect to {hostname}:{port} - {e}")
            self.send_error(502, f"Could not connect to {hostname}:{port}")
            return

        self.send_response(200, 'Connection Established')
        self.end_headers()

        sockets = [self.connection, dest_socket]
        try:
            while True:
                readable, _, exceptional = select.select(sockets, [], sockets, 15)
                if exceptional or not readable:
                    break
                
                for sock in readable:
                    other_sock = dest_socket if sock is self.connection else self.connection
                    data = sock.recv(8192)
                    if not data:
                        if sock in sockets: sockets.remove(sock)
                        if other_sock in sockets: sockets.remove(other_sock)
                        break
                    other_sock.sendall(data)
        except socket.error as e:
            pass
        finally:
            print(f"[PROXY LOG] Closing tunnel to {hostname}:{port}")
            for sock in sockets:
                sock.close()

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')
        
    def do_HEAD(self):
        self.handle_request('HEAD')

    def do_OPTIONS(self):
        self.handle_request('OPTIONS')

    def handle_request(self, method):
        is_cacheable_method = method == 'GET'
        
        url = self.path
        if not url.startswith(('http://', 'https://')):
            self.send_error(400, "Bad URL format")
            return
            
        print(f"[PROXY LOG] Request received: {method} {url}")
        
        try:
            parsed_url = urllib.parse.urlparse(url)
            hostname = parsed_url.hostname
            if not hostname:
                self.send_error(400, "Bad URL")
                return

            is_whitelisted = any(hostname == d or hostname.endswith("." + d) for d in WHITELIST)
            cache_file_path = None

            if is_whitelisted and is_cacheable_method:
                sanitized_path = parsed_url.path.lstrip('/')
                cache_file_path = os.path.join(CACHE_PATH, hostname, sanitized_path)
                
                if not sanitized_path or sanitized_path.endswith('/'):
                    cache_file_path = os.path.join(cache_file_path, 'index.html')

                if os.path.commonprefix((os.path.realpath(cache_file_path), os.path.realpath(CACHE_PATH))) != os.path.realpath(CACHE_PATH):
                    print("[PROXY LOG] WARNING: Potential directory traversal attempt blocked.")
                    self.send_error(400, "Bad Request")
                    return

                print(f"[PROXY LOG] Whitelisted. Checking cache for: {cache_file_path}")

                if os.path.exists(cache_file_path) and not os.path.isdir(cache_file_path):
                    try:
                        with open(cache_file_path, 'rb') as f:
                            content = f.read()
                        print(f"[PROXY LOG] CACHE HIT: Serving from {cache_file_path}")
                        self.send_response(200)
                        mimetype, _ = mimetypes.guess_type(cache_file_path)
                        if mimetype:
                            self.send_header('Content-type', mimetype)
                        self.send_header('Content-Length', str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                        return
                    except Exception as e:
                        print(f"[PROXY LOG] ERROR: Could not serve from cache: {e}")

            self.proxy_to_web(method, url, cache_file_path, is_whitelisted and is_cacheable_method)

        except Exception as e:
            self.send_error(500, f"Internal Proxy Error: {e}")
            print(f"[PROXY LOG] ERROR: Internal proxy error on {url}: {e}")

    def proxy_to_web(self, method, url, cache_path, should_cache):
        if should_cache:
            print(f"[PROXY LOG] CACHE MISS: Proxying {url} to the web.")
        else:
            print(f"[PROXY LOG] Proxying non-cacheable request: {method} {url}")

        final_url = url
        if url.startswith('http://'):
            final_url = 'https' + url[4:]
            print(f"[PROXY LOG] Upgrading request to HTTPS: {final_url}")
            
        try:
            req_headers = {key: value for key, value in self.headers.items() if key.lower() not in ['host', 'proxy-connection']}
            
            post_data = None
            if method in ['POST', 'PUT', 'PATCH']:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)

            with requests.request(method, final_url, headers=req_headers, data=post_data, stream=True, timeout=20) as resp:
                self.send_response(resp.status_code)
                
                content = bytearray()
                for key, value in resp.headers.items():
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection', 'strict-transport-security']:
                        self.send_header(key, value)
                
                for chunk in resp.iter_content(chunk_size=8192):
                    content.extend(chunk)

                self.send_header('Content-Length', str(len(content)))
                self.end_headers()

                if method != 'HEAD':
                    self.wfile.write(content)

                if should_cache and resp.status_code == 200 and cache_path:
                    try:
                        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                        with open(cache_path, 'wb') as f:
                            f.write(content)
                        print(f"[PROXY LOG] CACHED: Saved response from {url} to {cache_path}")
                    except Exception as e:
                        print(f"[PROXY LOG] ERROR: Could not write to cache file {cache_path}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"[PROXY LOG] ERROR: Proxy request for {url} failed: {e}")
            self.send_error(502, f"Proxy Error: {e}")


def start_proxy_server(host, port):
    server = socketserver.ThreadingTCPServer((host, port), CachingProxy, bind_and_activate=False)
    server.allow_reuse_address = True
    try:
        server.server_bind()
        server.server_activate()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"Proxy server started on {host}:{port}")
    except Exception as e:
        print(f"Could not start proxy server on {host}:{port}: {e}")
        return False
    return True

if __name__ == '__main__':
    if not os.path.exists(DOMAINS_PATH):
        print(f"Can't find domains whitelist \"{DOMAINS_PATH}\" ;(")

    with open(DOMAINS_PATH, "r") as f:
        WHITELIST = json.load(f)

    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    
    if start_proxy_server(PROXY_HOST, PROXY_PORT):
        proxy_url = f"http://{PROXY_HOST}:{PROXY_PORT}"
        os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = f"--proxy-server={proxy_url}"
    else:
        print("WARNING: Proxy failed to start. Caching will be disabled.")

    window = webview.create_window(
        "PenguinMod Desktop",
        "http://studio.penguinmod.com/editor.html",
        width=1024,
        height=780,
        min_size=(1024, 768)
    )

    webview.start(debug=True)
