import os

class Config:
    def __init__(self):
        self.directory = os.getcwd()  # Standardverzeichnis
        self.mysql_path = None
        self.java_path = "java"  # Standardpfad für Java-Interpreter
        self.certfile_path = None  # SSL-Zertifikatpfad
        self.keyfile_path = None  # SSL-Schlüsselpfad
        self.default_port = 8000
        self.settings_file = "server_settings.json"  # Einstellungsdatei
