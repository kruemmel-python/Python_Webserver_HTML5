# Python Webserver GUI für HTML5 und Dateiverwaltung

Dieses Projekt ist eine grafische Benutzeroberfläche (GUI) für einen erweiterten Python-Webserver, der die Verwaltung von HTML5-Dateien und anderen Dateitypen ermöglicht. Die Anwendung unterstützt das Hochladen und Herunterladen von Dateien, die Verwaltung von SSL-Zertifikaten, die Integration von MySQL und Java sowie das Setzen von Dateiberechtigungen.

## Inhaltsverzeichnis

- [Installation](#installation)
- [Verwendung](#verwendung)
- [Funktionen](#funktionen)
- [Unterstützte Dateitypen](#unterstützte-dateitypen)
- [Konfiguration](#konfiguration)
- [Beiträge](#beiträge)
- [Lizenz](#lizenz)

## Installation

1. Klone das Repository:
    ```sh
   https://github.com/kruemmel-python/Python_Webserver_HTML5.git
    ```

2. Navigiere in das Projektverzeichnis:
    ```sh
    cd Python_Webserver_HTML5
    ```

3. Installiere die erforderlichen Abhängigkeiten:
    ```sh
    pip install -r requirements.txt
    ```

## Verwendung

1. Starte die Anwendung:
    ```sh
    python main.py
    ```

2. Die GUI wird angezeigt. Du kannst nun die verschiedenen Einstellungen konfigurieren und den Server starten oder stoppen.

## Funktionen

- **Server-Steuerung**: Starten und Stoppen des Webservers.
- **Einstellungen**: Speichern, Laden und Löschen der Einstellungen.
- **Verzeichnisauswahl**: Auswahl des Stammverzeichnisses und des Download-Verzeichnisses.
- **Dateiverwaltung**: Auflisten, Hochladen und Herunterladen von Dateien.
- **SSL-Zertifikate**: Verwaltung von SSL-Zertifikaten und -Schlüsseln.
- **Berechtigungen**: Setzen von Dateiberechtigungen.
- **MySQL-Integration**: Konfiguration des MySQL-Pfads.
- **Java-Integration**: Auswahl des Java-Interpreters und Ausführung von Java-Dateien.

## Unterstützte Dateitypen

Der Webserver unterstützt eine Vielzahl von Dateitypen, darunter:

- **HTML5**: Standard-Webseiten.
- **Bilder**: PNG, JPG, GIF, BMP, TIF, ICO.
- **Audio**: MP3, FLAC, OGG, WAV.
- **Dokumente**: DOCX, PPTX, XLSX, ODT, ODS.
- **Archive**: ZIP.
- **Jupyter Notebooks**: IPYNB.
- **Textdateien**: TXT.
- **Java-Dateien**: JAVA.

## Konfiguration

Die Konfiguration wird in einer JSON-Datei (`server_settings.json`) gespeichert. Diese Datei enthält Einstellungen wie das Stammverzeichnis, den MySQL-Pfad, den Java-Pfad, die SSL-Zertifikat- und Schlüsselpfade sowie den Standardport.

### Beispiel für `server_settings.json`:
```json
{
    "directory": "/path/to/directory",
    "mysql_path": "/path/to/mysql",
    "java_path": "/path/to/java",
    "certfile_path": "/path/to/certfile.pem",
    "keyfile_path": "/path/to/keyfile.pem",
    "port": 8000
}
```

## Beiträge

Beiträge sind willkommen! Wenn du einen Fehler findest oder eine Verbesserung vorschlagen möchtest, erstelle bitte ein Issue oder einen Pull Request.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen findest du in der [LICENSE](LICENSE) Datei.
```
