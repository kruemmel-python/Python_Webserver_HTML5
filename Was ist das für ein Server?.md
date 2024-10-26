---

Dieses Programm stellt eine benutzerfreundliche Server-GUI dar, mit der Benutzer einen Webserver starten und verwalten können, um HTML5-Webseiten zu hosten. Es eignet sich besonders für Einsteiger und Nutzer, die schnell und ohne tiefere Kenntnisse in der Serveradministration eine Entwicklungsumgebung für Webprojekte schaffen möchten.

### Funktionsumfang und Benutzeroberfläche des Servers

1. **Verzeichnis- und Port-Einstellungen**:
   - Der Server kann in einem festgelegten Stammverzeichnis gestartet werden, welches der Benutzer auswählen oder auf den Standardwert (`www`-Ordner) setzen kann.
   - Benutzer können den Port konfigurieren, auf dem der Server lauschen soll (Standardwert ist `8000`).

2. **GUI-gestützte Verzeichnisnavigation und -Verwaltung**:
   - Die GUI ermöglicht es, den Inhalt des Stammverzeichnisses und von Unterordnern zu durchsuchen. Benutzer können durch Doppelklicks in Ordner navigieren und im Verzeichnisbaum Dateien und Ordner anzeigen.
   - Ein „Zurück“-Button erlaubt die einfache Navigation in übergeordnete Verzeichnisse.

3. **Berechtigungen festlegen**:
   - Die Benutzeroberfläche bietet Schaltflächen zum Setzen von Berechtigungen (Lesen, Schreiben, Ausführen) für Dateien und Ordner. Die aktuellen Berechtigungen jeder Datei werden übersichtlich angezeigt.

4. **MySQL und Java-Integration**:
   - Der Server bietet die Möglichkeit, externe Programme wie MySQL und Java zu integrieren. Benutzer können die Pfade zu diesen Anwendungen in der GUI festlegen, sodass der Server auf Java-Dateien zugreifen und MySQL für datenbankgestützte Webanwendungen verwenden kann.
   - Java-Dateien im Stammverzeichnis können direkt durch den Server kompiliert und ausgeführt werden, was eine einfache Testumgebung für Java-Webanwendungen ermöglicht. Ein weiteres Highlight ist die Möglichkeit, Java-Dateien direkt über eine HTML-Seite zu testen: 

       **HTML-Seite für Java-Code-Tests**: Eine im Server integrierte HTML-Seite bietet ein Textfeld für Java-Code und eine Ausführen-Schaltfläche. Der eingegebene Code wird an den Server gesendet, kompiliert, ausgeführt und die Ausgabe direkt im Browser angezeigt. Dies erleichtert die schnelle Java-Entwicklung und das Testen von Java-Code in einer browserbasierten Umgebung.

5. **SSL-Zertifikat- und Schlüsselverwaltung**:
   - Um eine sichere Verbindung zu gewährleisten, können Benutzer SSL-Zertifikate und -Schlüssel auswählen. Diese ermöglichen es, den Server bei Bedarf über HTTPS abzusichern.

6. **Datei-Upload und Verwaltung**:
   - Dateien können direkt über die GUI auf den Server hochgeladen werden. Der Upload erfolgt im „downloads“-Ordner, welcher automatisch im Stammverzeichnis erstellt wird. 
   - Der Server unterstützt zusätzlich den Upload und die Anzeige einer Dateiliste über `/file-list`.

7. **Serverstart und -stopp**:
   - Die GUI bietet Schaltflächen zum Starten und Stoppen des Servers. Ein Label zeigt den aktuellen Serverstatus an („Server läuft“ oder „Server gestoppt“), was die Bedienung übersichtlich und nutzerfreundlich gestaltet.

8. **Erweiterte Fehlerbehandlung und Logging**:
   - Der Server speichert Ereignisse und Fehler in einer Log-Datei, was bei der Fehlersuche oder für die Analyse der Serveraktivitäten nützlich ist.
   - Ein Rotations-Logging-System stellt sicher, dass die Log-Datei nicht übermäßig wächst und bei Bedarf ältere Logs automatisch gelöscht werden.

9. **Einstellungsspeicherung und -verwaltung**:
   - Alle Einstellungen wie Pfade, Port und Zertifikate werden in einer JSON-Datei gespeichert und können beim Start des Programms geladen werden. Dies ermöglicht, dass der Server bei jedem Neustart dieselben Einstellungen nutzt und den Aufwand für den Benutzer minimiert.
   - Benutzer können Einstellungen löschen, was die Konfiguration auf die Standardwerte zurücksetzt.

### Eignung und Einsatzbereich

Dieser Server eignet sich hervorragend für Entwickler, die eine einfache Testumgebung für Webprojekte benötigen, insbesondere für Projekte, die HTML5, Java oder MySQL nutzen. Die Benutzeroberfläche ermöglicht die Verwaltung und Navigation im Dateisystem und bietet dennoch die Option, Dateien hochzuladen, Rechte zu verwalten und sogar Java-Dateien zu kompilieren und auszuführen. Die Integration der HTML5-basierten Java-Testseite erweitert die Funktionalität erheblich und ermöglicht Java-Tests direkt im Browser. 

Die Integration von SSL und die Möglichkeit, verschiedene Anwendungen wie MySQL zu verbinden, machen ihn auch für fortgeschrittenere Projekte interessant.
