<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Listado de Expedientes</title>
        <style>
            #expedientes {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }

            .expediente {
                border: 1px solid #ccc;
                padding: 10px;
                width: 200px;
                cursor: pointer;
            }
            body{
                background-color: #3498db;
            }
            .fondo {
                position: absolute;
                justify-content: center;
                align-items: center;
                width: 90%;
                height: 100%;
                border-radius: 10px;
                top: 52%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                background-color: white;
                z-index: 1;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }
            a.regresar {
                margin-left: 40px; 
                text-decoration: none;
                color: #0077B5;
                font-weight: bold;
                font-size: 16px;
                background-color: #0077B5;
                padding: 8px 12px; 
                border-radius: 4px; 
                color: #fff;
                transition: background-color 0.3s, color 0.3s, border-color 0.3s;
            }
        </style>
    </head>
    <body>
        <div class="fondo"> 
            <a class="regresar" href="ALTA_EXPEDIENTE.php">Agregar expediente</a>
            <div id="expedientes">
                <!-- Ejemplo de expediente -->
                <div class="expediente" onclick="verExpediente(1, 'Nombre del Paciente', 'Nombre del Doctor', '2023-01-01 12:00:00')">
                    <p>ID del Expediente:</p>
                    <p>Nombre del Paciente: Nombre del Paciente</p>
                    <p>Doctor: Nombre del Doctor</p>
                    <p>Fecha y Hora: 2023-01-01 12:00:00</p>
                </div>
            </div>

            <!-- Mensaje cuando no hay expedientes -->
            <div id="mensajeNoExpedientes" style="display:none;">
                <p>No tienes ningún expediente para visualizar.</p>
            </div>


            <script>
                function verExpediente(idExpediente, nombrePaciente, nombreDoctor, fechaHora) {
                    window.location.href = 'DETALLE_EXPEDIENTE.php?id=' + idExpediente;
                }
                var expedientes = [
                    { id: 1, paciente: 'Nombre del Paciente 1', doctor: 'Nombre del Doctor 1', fechaHora: '2023-01-01 12:00:00' },
                    { id: 2, paciente: 'Nombre del Paciente 2', doctor: 'Nombre del Doctor 2', fechaHora: '2023-02-01 14:30:00' },
                ];
                var mensajeNoExpedientes = document.getElementById('mensajeNoExpedientes');
                if (expedientes.length === 0) {
                    mensajeNoExpedientes.style.display = 'block';
                } else {
                    mensajeNoExpedientes.style.display = 'none';
                }


                var contenedorExpedientes = document.getElementById('expedientes');
                expedientes.forEach(function (expediente) {
                    var bloqueExpediente = document.createElement('div');
                    bloqueExpediente.className = 'expediente';
                    bloqueExpediente.innerHTML = `
                    <p>ID del Expediente: ${expediente.id}</p>
                    <p>Nombre del Paciente: ${expediente.paciente}</p>
                    <p>Doctor: ${expediente.doctor}</p>
                    <p>Fecha y Hora: ${expediente.fechaHora}</p>
                    `;
                    bloqueExpediente.onclick = function () {
                        verExpediente(expediente.id, expediente.paciente, expediente.doctor, expediente.fechaHora);
                    };
                    contenedorExpedientes.appendChild(bloqueExpediente);
                });
            </script>
        </div>
    </body>
</html>
