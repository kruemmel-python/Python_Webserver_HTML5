import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import stat
import json
import server_helpers

# Standardwerte
default_port = 8000
directory = os.path.join(os.getcwd(), "www")  # Hauptverzeichnis setzen
download_directory = os.path.join(directory, "downloads")
mysql_path = None
java_path = "java"  # Standardpfad für Java-Interpreter
certfile_path = None  # Pfad zum SSL-Zertifikat
keyfile_path = None  # Pfad zum SSL-Schlüssel
settings_file = "server_settings.json"  # Einstellungsdatei

# Erstelle den downloads-Ordner, falls er nicht existiert
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Funktion zum Laden der Einstellungen aus einer JSON-Datei
def load_settings():
    global directory, mysql_path, java_path, certfile_path, keyfile_path, default_port
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as file:
                settings = json.load(file)
                directory = settings.get("directory", os.getcwd())
                mysql_path = settings.get("mysql_path", None)
                java_path = settings.get("java_path", "java")
                certfile_path = settings.get("certfile_path", None)
                keyfile_path = settings.get("keyfile_path", None)
                default_port = settings.get("port", 8000)
                # GUI-Elemente aktualisieren
                directory_label.config(text=f"Stammverzeichnis: {directory}")
                mysql_label.config(text=f"MySQL-Pfad: {mysql_path}")
                java_label.config(text=f"Java-Pfad: {java_path}")
                certfile_label.config(text=f"Zertifikat: {certfile_path}")
                keyfile_label.config(text=f"Schlüssel: {keyfile_path}")
                port_entry.delete(0, tk.END)
                port_entry.insert(0, str(default_port))
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Einstellungen: {e}")

# Funktion zum Speichern der Einstellungen in einer JSON-Datei
def save_settings():
    settings = {
        "directory": directory,
        "mysql_path": mysql_path,
        "java_path": java_path,
        "certfile_path": certfile_path,
        "keyfile_path": keyfile_path,
        "port": port_entry.get()
    }
    try:
        with open(settings_file, "w") as file:
            json.dump(settings, file)
        directory_label.config(text=f"Stammverzeichnis: {directory}")  # GUI aktualisieren
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der Einstellungen: {e}")

# Funktion zum Löschen der Einstellungsdatei
def delete_settings():
    if os.path.exists(settings_file):
        try:
            os.remove(settings_file)
            messagebox.showinfo("Erfolgreich", "Einstellungsdatei gelöscht.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen der Einstellungsdatei: {e}")
    else:
        messagebox.showinfo("Info", "Einstellungsdatei existiert nicht.")

# Funktionen zur Auswahl von Dateien und Verzeichnissen
def select_directory():
    global directory
    directory = filedialog.askdirectory(initialdir=directory)
    if directory:
        directory_label.config(text=f"Stammverzeichnis: {directory}")
        list_directory_contents()

def select_mysql():
    global mysql_path
    mysql_path = filedialog.askopenfilename(filetypes=[("MySQL", "mysql*"), ("Alle Dateien", "*.*")])
    mysql_label.config(text=f"MySQL-Pfad: {mysql_path}")

def select_java():
    global java_path
    java_path = filedialog.askopenfilename(filetypes=[("Java", "java*"), ("Alle Dateien", "*.*")])
    java_label.config(text=f"Java-Pfad: {java_path}")

def select_certfile():
    global certfile_path
    certfile_path = filedialog.askopenfilename(filetypes=[("PEM-Zertifikat", "*.pem"), ("Alle Dateien", "*.*")])
    certfile_label.config(text=f"Zertifikat: {certfile_path}")

def select_keyfile():
    global keyfile_path
    keyfile_path = filedialog.askopenfilename(filetypes=[("PEM-Schlüssel", "*.pem"), ("Alle Dateien", "*.*")])
    keyfile_label.config(text=f"Schlüssel: {keyfile_path}")

# Funktion zum Auflisten der Verzeichnisinhalte
def list_directory_contents():
    file_tree.delete(*file_tree.get_children())
    if os.path.isdir(directory):
        items = os.listdir(directory)
        for item in items:
            full_path = os.path.join(directory, item)
            permissions = get_file_permissions(full_path)
            file_type = "Ordner" if os.path.isdir(full_path) else os.path.splitext(item)[1][1:].upper() if os.path.splitext(item)[1] else "Datei"
            file_tree.insert("", "end", iid=full_path, values=(item, permissions, file_type))

def get_file_permissions(path):
    st_mode = os.stat(path).st_mode
    perms = (
        ("r" if st_mode & stat.S_IRUSR else "-") +
        ("w" if st_mode & stat.S_IWUSR else "-") +
        ("x" if st_mode & stat.S_IXUSR else "-") +
        ("r" if st_mode & stat.S_IRGRP else "-") +
        ("w" if st_mode & stat.S_IWGRP else "-") +
        ("x" if st_mode & stat.S_IXGRP else "-") +
        ("r" if st_mode & stat.S_IROTH else "-") +
        ("w" if st_mode & stat.S_IWOTH else "-") +
        ("x" if st_mode & stat.S_IXOTH else "-")
    )
    return perms

def set_permissions():
    selected = file_tree.selection()
    if not selected:
        messagebox.showinfo("Info", "Bitte wählen Sie eine Datei oder einen Ordner aus.")
        return

    full_path = selected[0]
    read_perm = read_var.get()
    write_perm = write_var.get()
    execute_perm = execute_var.get()

    new_perms = (
        (stat.S_IRUSR if read_perm else 0) |
        (stat.S_IWUSR if write_perm else 0) |
        (stat.S_IXUSR if execute_perm else 0)
    )

    try:
        os.chmod(full_path, new_perms)
        list_directory_contents()
        messagebox.showinfo("Erfolgreich", f"Berechtigungen für {os.path.basename(full_path)} wurden gesetzt.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Berechtigungen konnten nicht gesetzt werden: {e}")

# Funktion zum Wechseln in einen Ordner
def change_directory(event):
    global directory
    selected = file_tree.selection()
    if not selected:
        return

    full_path = selected[0]
    if os.path.isdir(full_path):
        directory = full_path
        directory_label.config(text=f"Stammverzeichnis: {directory}")
        list_directory_contents()

# Funktion zum Zurückkehren zum übergeordneten Verzeichnis
def go_back():
    global directory
    parent_directory = os.path.dirname(directory)
    if parent_directory != directory:
        directory = parent_directory
        directory_label.config(text=f"Stammverzeichnis: {directory}")
        list_directory_contents()

# Funktion zum Beenden des Servers und Schließen des Fensters
def on_closing():
    server_helpers.stop_server()
    save_settings()
    app.destroy()

# GUI erstellen
app = tk.Tk()
app.title("Python Webserver GUI")

# Menü erstellen
menu = tk.Menu(app)
app.config(menu=menu)

# Menüpunkt "Einstellungen" hinzufügen
settings_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Einstellungen", menu=settings_menu)
settings_menu.add_command(label="Speichern", command=save_settings)
settings_menu.add_command(label="Löschen", command=delete_settings)
settings_menu.add_separator()
settings_menu.add_command(label="Beenden", command=on_closing)

# Port-Einstellung
tk.Label(app, text="Server Port:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
port_entry = tk.Entry(app)
port_entry.insert(0, str(default_port))
port_entry.grid(row=0, column=1, padx=10, pady=5)

# Stammverzeichnis-Auswahl
directory_label = tk.Label(app, text=f"Stammverzeichnis: {directory}")
directory_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
tk.Button(app, text="Verzeichnis auswählen", command=select_directory).grid(row=1, column=2, padx=10, pady=5)

# MySQL-Pfad-Auswahl
mysql_label = tk.Label(app, text="MySQL-Pfad: Nicht ausgewählt")
mysql_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
tk.Button(app, text="MySQL auswählen", command=select_mysql).grid(row=2, column=2, padx=10, pady=5)

# Java-Pfad-Auswahl
java_label = tk.Label(app, text="Java-Pfad: Nicht ausgewählt")
java_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")
tk.Button(app, text="Java auswählen", command=select_java).grid(row=3, column=2, padx=10, pady=5)

# SSL-Zertifikat-Auswahl
certfile_label = tk.Label(app, text="Zertifikat: Nicht ausgewählt")
certfile_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")
tk.Button(app, text="Zertifikat auswählen", command=select_certfile).grid(row=4, column=2, padx=10, pady=5)

# SSL-Schlüssel-Auswahl
keyfile_label = tk.Label(app, text="Schlüssel: Nicht ausgewählt")
keyfile_label.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")
tk.Button(app, text="Schlüssel auswählen", command=select_keyfile).grid(row=5, column=2, padx=10, pady=5)

# Datei- und Ordnerliste
file_tree = ttk.Treeview(app, columns=("name", "permissions", "type"), show="headings")
file_tree.heading("name", text="Name")
file_tree.heading("permissions", text="Berechtigungen")
file_tree.heading("type", text="Typ")
file_tree.grid(row=6, column=0, columnspan=3, padx=10, pady=5)
file_tree.bind("<Double-1>", change_directory)  # Doppelklick zum Wechseln in einen Ordner

# Zurück-Button
tk.Button(app, text="Zurück", command=go_back).grid(row=7, column=0, padx=10, pady=5)

# Berechtigungen setzen
read_var = tk.BooleanVar()
write_var = tk.BooleanVar()
execute_var = tk.BooleanVar()

tk.Checkbutton(app, text="Lesen", variable=read_var).grid(row=8, column=0, sticky="w", padx=10)
tk.Checkbutton(app, text="Schreiben", variable=write_var).grid(row=8, column=1, sticky="w", padx=10)
tk.Checkbutton(app, text="Ausführen", variable=execute_var).grid(row=8, column=2, sticky="w", padx=10)

tk.Button(app, text="Berechtigungen setzen", command=set_permissions).grid(row=9, column=0, columnspan=3, padx=10, pady=10)

# Server-Steuerung
tk.Button(app, text="Server starten", command=server_helpers.start_server, bg="green", fg="white").grid(row=10, column=0, padx=10, pady=20)
tk.Button(app, text="Server stoppen", command=server_helpers.stop_server, bg="red", fg="white").grid(row=10, column=1, padx=10, pady=20)

# Serverstatus-Label
status_label = tk.Label(app, text="Server ist gestoppt", fg="red")
status_label.grid(row=11, column=0, columnspan=3, pady=10)

def update_status(status):
    if status == "running":
        status_label.config(text="Server läuft", fg="green")
    else:
        status_label.config(text="Server ist gestoppt", fg="red")

# Initialisierung und Laden der Einstellungen
list_directory_contents()
load_settings()
app.protocol("WM_DELETE_WINDOW", on_closing)  # Einstellungen speichern und Server beenden beim Schließen
app.mainloop()
