<html>
    <head>
        <title>Crear expediente</title>
        <style>

            h1 {
                font-size: 35px;
                color: #333;
                font-weight: bold;
                text-transform: uppercase;
                margin: 40px;
                margin-left: -80px;
            }
            .tabla {
                display: flex;
                justify-content: center;
            }
            .columna {
                flex: 1;
                border: 1px;
            }
            .columna:nth-child(2) {
                flex: 0.3;
            }

            .cajas{
                text-align: left;
            }
            .divs{
                display: flex;
                justify-content: center;
            }
            input[type="text"],
            textarea {
                padding: 14.5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
                width: 200px;
                height: 25px;
            }
            p {
                font-family: "Arial", sans-serif;
            }
            input[type="submit"] {
                display: inline-block;
                margin-left: 150px;
                margin-top: -20px;
                padding: 7px 15px;
                font-size: 16px;
                text-decoration: none;
                background-color: #3498db;
                color: #fff;
                border: 1px solid #3498db;
                border-radius: 5px;
                cursor: pointer;
                justify-content: center;
                text-align: center;
                transition: background-color 0.3s, color 0.3s;
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
            #popup {
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                padding: 20px;
                background-color: #fff;
                border: 1px solid #ccc;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                z-index: 1000;
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
        <script>
            function mostrarVentanaEmergente() {
                document.getElementById('popup').style.display = 'block';
            }
            function cerrarVentanaEmergente() {
                document.getElementById('popup').style.display = 'none';
            }
            function preguntaCompartir() {
                cerrarVentanaEmergente();
                var compartirPopup = window.open('', 'Compartir Expediente', 'width=400,height=300');
                compartirPopup.document.write(`
                <html>
                <head>
                    <title>Compartir Expediente</title>
                </head>
                <body>
                    <p>¿Desea compartir el expediente?</p>
                    <form>
                    <label for="nombreUsuario">Nombre de Usuario:</label>
                    <input type="text" id="nombreUsuario" name="nombreUsuario" placeholder="Ingresa el nombre del usuario" required><br>
                    <label for="privilegios">Privilegios:</label>
                    <select id="privilegios" name="privilegios">
                        <option value="ver">Ver</option>
                        <option value="modificar">Modificar</option>
                    </select><br>
                    <button type="button" onclick="compartirExpediente()">Compartir</button>
                    </form>
                </body>
                </html>
                `);
            }
        </script>

    </head>
    <body>
        <div class="fondo">
        <a class="regresar" href="LISTA_EXPEDIENTE.php">Regresar a la lista</a>
        <form id="Form01" name="Form01" valign="center" align="middle">
            <div class="tabla">
            <H1>Expediente medico</H1>
                <div class="columna cajas">
                    <br><p>Nombre del doctos que creo el expediente</p><br>
                    <br><p>Datos de alta</p>
                    <input type="text" name="fechaHora" id="fechaHora" placeholder="fecha y hora..."/>
                    <input type="text" style="width:60px;height:10px" name="numConsul" id="numConsul" placeholder="N° de consultorio..."/>
                    <input type="text" style="width:60px;height:10px" name="IdExp" id="IdExp" placeholder="ID del expediente..."/><br>
                    <input type="text" name="motivoConsul" id="motivoConsul" placeholder="motivo de la cita..."/><br>
                    <br><p>Datos personales</p>
                    <input type="text" name="nombre" id="nombre" placeholder="Nombre completo"/>
                    <input type="text" style="width:60px;height:10px" name="sexo" id="sexo" placeholder="Sexo"/>
                    <input type="text" style="width:60px;height:10px" name="edad" id="edad" placeholder="Edad"/><br>
                    <input type="text" name="domicilio" id="domicilio" placeholder="Domicilio"/>
                    <input type="text" name="telefono" id="telefono" placeholder="Telefono"/><br>
                    <br><p>Datos de salud</p>
                    <textarea  style="width:600px;height:80px" data-component="textarea" placeholder="Historial clinico.." aria-labelledby="label_26"></textarea><br>
                    <br><p>Observaciones</p>
                    <textarea  style="width:600px;height:80px" data-component="textarea" aria-labelledby="label_26"></textarea><br><br>
                    
                    <form enctype="multipart/form-data" action="salva_archivo.php" method="post">
                        <input type="file" id="archivo" name="archivo">
                    </form>
                </div>
                
            </div>
            <input type="submit" onclick="mostrarVentanaEmergente()" value="Guardar expediente"/><br><br>           
        </form>    
        </div>
       
    </body>
    <div id="popup">
        <p>¿Desea continuar con el guardado?</p><br>
        <button onclick="preguntaCompartir()">Sí</button>
        <button onclick="cerrarVentanaEmergente()">No</button>
    </div>
</html>