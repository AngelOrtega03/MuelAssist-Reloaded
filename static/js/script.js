function examinarFoto() {
    document.getElementById('file-input').click();
}

function mostrarImagen(input) {
    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('profile-image').src = e.target.result;
    };
    reader.readAsDataURL(input.files[0]);
}

function verCitas() {
    // Agrega la lógica para ver las citas
    alert("Ver Citas");
}

function actualizarDatos() {
    // Agrega la lógica para actualizar los datos
    alert("Actualizar Datos");
}
