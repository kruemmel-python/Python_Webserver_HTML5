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
import re

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

    # Video-Dateien
    elif file_content[4:8] == b'ftyp':
        # MP4-Datei (prüfen auf ftyp Box im Header)
        if file_content[8:12] in [b'isom', b'iso2', b'avc1', b'mp41', b'mp42']:
            return ".mp4"
    elif file_content.startswith(b'RIFF') and file_content[8:12] == b'AVI ':
        # AVI-Datei
        return ".avi"
    elif file_content.startswith(b'\x1A\x45\xDF\xA3'):
        # WebM-Datei (Teil von Matroska-Format)
        return ".webm"
    elif file_content.startswith(b'\x30\x26\xB2\x75\x8E\x66\xCF\x11'):
        # WMV-Datei (Microsoft Advanced Systems Format)
        return ".wmv"
    
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
            # Direktes Ausführen einer angeforderten Java-Datei
            java_file = self.translate_path(self.path)
            class_name = os.path.splitext(os.path.basename(java_file))[0]
            self.execute_java(java_file, class_name)
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

    def execute_java(self, java_file, class_name):
        # Verwenden des vollständigen Pfads zu `javac` und `java`
        java_home_path = os.path.dirname(gui_helpers.java_path)
        javac_path = os.path.join(java_home_path, "javac")
        java_exec_path = os.path.join(java_home_path, "java")

        logging.info(f"Verwende javac-Pfad: {javac_path}")
        logging.info(f"Verwende java-Pfad: {java_exec_path}")

        # Kompilieren der Java-Datei
        compile_process = subprocess.run(
            [javac_path, "--release", "8", java_file],
            capture_output=True, text=True
        )
    
        # Filtern der Fehlermeldung, nur Zeilen mit dem Begriff "Fehler" behalten
        error_lines = "\n".join(
            line for line in compile_process.stderr.splitlines() if "Fehler" in line
        )
    
        if compile_process.returncode != 0:
            # Rückgabe nur der gefilterten Fehlermeldungen an den Client
            error_message = f"Kompilierungsfehler:\n{error_lines}"
            logging.error(error_message)
            self.send_response(400)  # Statuscode 400 für Bad Request
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(error_message.encode('utf-8'))
            return

        # Ausführen der kompilierten Java-Klasse
        run_process = subprocess.run(
            [java_exec_path, "-cp", os.path.dirname(java_file), class_name],
            capture_output=True, text=True
        )
        if run_process.returncode != 0:
            # Rückgabe des Laufzeitfehlers an den Client
            error_message = f"Fehler bei der Ausführung:\n{run_process.stderr}"
            logging.error(error_message)
            self.send_response(500)  # Statuscode 500 für internen Serverfehler
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(error_message.encode('utf-8'))
            return

        # Rückgabe der erfolgreichen Ausgabe
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(run_process.stdout.encode('utf-8'))



    def do_POST(self):
        if self.path == "/execute-java":
            self.handle_java_execution()
        elif self.path == "/upload":
            content_type, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if content_type == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-Length'))
                form_data = cgi.parse_multipart(self.rfile, pdict)
                if 'file' in form_data:
                    # Speichern der Datei
                    self.save_uploaded_file(form_data['file'][0])
                else:
                    self.send_error(400, "Keine Datei im Upload gefunden.")
            else:
                self.send_error(400, "Ungültiger Content-Type für Upload.")

    def handle_java_execution(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            code = data.get("code")
            if code:
                # Extrahiere den Klassennamen
                match = re.search(r'public class (\w+)', code)
                if not match:
                    self.send_error(400, "Java-Klassennamen konnte nicht gefunden werden.")
                    return
                class_name = match.group(1)

                # Speichern des Java-Codes in einer temporären Datei mit dem Klassennamen
                java_file = os.path.join(directory, f"{class_name}.java")
                with open(java_file, "w") as f:
                    f.write(code)

                # Kompilieren und Ausführen des Java-Codes
                self.execute_java(java_file, class_name)
            else:
                self.send_error(400, "Kein Java-Code empfangen.")
        except Exception as e:
            self.send_error(500, f"Serverfehler: {str(e)}")


    def save_uploaded_file(self, file_content):
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
