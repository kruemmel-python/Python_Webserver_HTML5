// Datei hochladen
function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const statusText = document.getElementById('upload-status');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        statusText.textContent = 'Upload erfolgreich: ' + result;
        fileInput.value = ''; // Datei-Input zurücksetzen
        loadFileList(); // Datei-Liste aktualisieren
    })
    .catch(error => {
        statusText.textContent = 'Upload fehlgeschlagen: ' + error;
    });
}

// Liste verfügbarer Dateien laden
function loadFileList() {
    fetch('/file-list')
        .then(response => response.json())
        .then(files => {
            const fileList = document.getElementById('file-list');
            fileList.innerHTML = ''; // Datei-Liste zurücksetzen

            files.forEach(file => {
                const listItem = document.createElement('li');
                const downloadLink = document.createElement('a');
                downloadLink.href = '/downloads/' + file; // Pfad zur Datei
                downloadLink.textContent = file;
                downloadLink.download = file; // Ermöglicht das Herunterladen

                listItem.appendChild(downloadLink);
                fileList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Fehler beim Laden der Datei-Liste:', error));
}

// Datei-Liste beim Laden der Seite abrufen
window.onload = loadFileList;
