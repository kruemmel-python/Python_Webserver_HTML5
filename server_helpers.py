import http.server
import socketserver
import threading
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import ssl
import json
import socket
from tkinter import messagebox
import gui_helpers
import cgi
from datetime import datetime
import mimetypes
import stat

# Standardwerte und Konfigurationen
default_port = 8000
server_thread = None
settings_file = "server_settings.json"
log_handler = RotatingFileHandler('server.log', maxBytes=10000, backupCount=5)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(log_handler)

# Verzeichnis aus den Einstellungen laden
def load_directory():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            settings = json.load(file)
            return settings.get("directory", os.path.join(os.getcwd(), "www"))
    return os.path.join(os.getcwd(), "www")

# Setze das Hauptverzeichnis und den Downloads-Ordner
directory = load_directory()
download_directory = os.path.join(directory, "downloads")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Funktion zum Laden der Einstellungen aus der JSON-Datei
def load_settings():
    global directory, default_port
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as file:
                settings = json.load(file)
                directory = settings.get("directory", os.getcwd())
                default_port = settings.get("port", 8000)
                logging.info("Einstellungen erfolgreich geladen.")
        except Exception as e:
            logging.error(f"Fehler beim Laden der Einstellungen: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Einstellungen: {e}")

# Erweiterte Funktion zur Erkennung der Dateierweiterung basierend auf der Dateisignatur
def get_file_extension(file_content):
    if file_content.startswith(b'\x89PNG\r\n\x1a\n'):
        return ".png"
    elif file_content.startswith(b'\xFF\xD8\xFF'):
        return ".jpg"
    elif file_content[0:3] == b'GIF':
        return ".gif"
    elif file_content.startswith(b'BM'):
        return ".bmp"
    elif file_content.startswith(b'II*\x00') or file_content.startswith(b'MM\x00*'):
        return ".tif"
    elif file_content.startswith(b'\x00\x00\x01\x00') or file_content.startswith(b'\x00\x00\x02\x00'):
        return ".ico"
    elif file_content.startswith(b'ID3'):
        return ".mp3"
    elif file_content.startswith(b'fLaC'):
        return ".flac"
    elif file_content.startswith(b'OggS'):
        return ".ogg"
    elif file_content.startswith(b'RIFF') and file_content[8:12] == b'WAVE':
        return ".wav"
    elif file_content.startswith(b'%PDF'):
        return ".pdf"
    elif file_content[0:2] == b'PK':
        if b'word/' in file_content:
            return ".docx"
        elif b'ppt/' in file_content:
            return ".pptx"
        elif b'xl/' in file_content:
            return ".xlsx"
        elif b'odt' in file_content:
            return ".odt"
        elif b'ods' in file_content:
            return ".ods"
        else:
            return ".zip"
    elif file_content.startswith(b'{\n "cells"') or file_content.startswith(b'{"cells"'):
        return ".ipynb"
    elif file_content.startswith(b'\xEF\xBB\xBF'):
        return ".txt"
    else:
        return ".unknown"

# Serverklasse definieren
class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        # Wenn der Pfad mit /downloads/ beginnt, setze das richtige Verzeichnis
        if self.path.startswith("/downloads/"):
            # Konvertiere den Pfad, um auf den lokalen Dateisystempfad im downloads-Ordner zu verweisen
            relative_path = self.path[len("/downloads/"):]
            file_path = os.path.join(download_directory, relative_path)
            if os.path.isfile(file_path):
                # Sende die Datei aus dem downloads-Ordner
                self.send_response(200)
                self.send_header("Content-type", mimetypes.guess_type(file_path)[0] or "application/octet-stream")
                self.end_headers()
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File not found.")
        elif self.path.endswith(".java"):
            self.execute_java()
        elif self.path == "/file-list":
            self.send_file_list()
        else:
            # Standardverhalten für andere Pfade
            super().do_GET()

    def send_file_list(self):
        files = os.listdir(download_directory)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(files).encode("utf-8"))

    def execute_java(self):
        java_file = self.translate_path(self.path)
        if not os.path.exists(java_file):
            self.send_error(404, "Java-Datei nicht gefunden")
            return
        try:
            compile_process = subprocess.run(["javac", java_file], capture_output=True, text=True)
            if compile_process.returncode != 0:
                self.send_error(500, f"Kompilierungsfehler:\n{compile_process.stderr}")
                return
            java_class = os.path.splitext(os.path.basename(java_file))[0]
            run_process = subprocess.run(["java", "-cp", directory, java_class], capture_output=True, text=True)
            if run_process.returncode != 0:
                self.send_error(500, f"Fehler bei der Ausführung:\n{run_process.stderr}")
                return
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(run_process.stdout.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Serverfehler: {e}")

    def send_image(self):
        try:
            image_path = self.translate_path(self.path)
            with open(image_path, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", "image/png")
                self.end_headers()
                self.wfile.write(file.read())
        except Exception as e:
            self.send_error(404, "Bild nicht gefunden")

    def do_POST(self):
        if self.path == "/upload":
            content_type, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if content_type == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-Length'))
                form_data = cgi.parse_multipart(self.rfile, pdict)
                logging.info(f"Form data: {form_data}")
                if 'file' in form_data:
                    file_content = form_data['file'][0]
                    content_disposition = self.headers.get('Content-Disposition')
                    original_filename = "unknown_file"
                    if content_disposition:
                        _, params = cgi.parse_header(content_disposition)
                        original_filename = params.get('filename', 'unknown_file').strip('"')
                    file_extension = get_file_extension(file_content)
                    filename = f"{os.path.splitext(original_filename)[0]}{file_extension}"
                    file_path = os.path.join(download_directory, filename)
                    counter = 1
                    while os.path.exists(file_path):
                        filename = f"{os.path.splitext(original_filename)[0]}_{counter}{file_extension}"
                        file_path = os.path.join(download_directory, filename)
                        counter += 1
                    with open(file_path, 'wb') as output_file:
                        output_file.write(file_content)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b'Upload erfolgreich!')
                    logging.info(f"Datei {filename} erfolgreich hochgeladen")
                else:
                    logging.error("Keine Datei im Upload gefunden.")
                    self.send_error(400, "Keine Datei im Upload gefunden.")
            else:
                logging.error(f"Ungültiger Content-Type für Upload: {content_type}")
                self.send_error(400, "Ungültiger Content-Type für Upload.")

# ThreadingTCPServer für parallele Anfragen
class MyTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

def start_server():
    global server_thread
    if server_thread and server_thread.is_alive():
        messagebox.showinfo("Info", "Server läuft bereits.")
        return
    try:
        port = int(gui_helpers.port_entry.get())
        Handler = MyHTTPRequestHandler
        httpd = MyTCPServer(("", port), Handler)
        logging.info(f"Server startet auf Port {port}")
        gui_helpers.update_status("running")
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
    except Exception as e:
        logging.error(f"Server konnte nicht gestartet werden: {e}")

def stop_server():
    global server_thread
    if server_thread and server_thread.is_alive():
        server_thread = None
        gui_helpers.update_status("stopped")
        messagebox.showinfo("Server gestoppt", "Der Server wurde gestoppt.")

def find_free_port(start_port=default_port):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1
