from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from assets.passcheck import password_check
from datetime import datetime


app = Flask(__name__)


app.secret_key = 'your secret key'

#Conexion con la base de datos
app.config['MYSQL_HOST'] = '146.190.218.21'
app.config['MYSQL_USER'] = 'muelitas'
app.config['MYSQL_PASSWORD'] = 'CONTRASENIAENMINUSCULAS'
app.config['MYSQL_DB'] = 'muelassist_sql'

mysql = MySQL(app)

#Rutas de la pagina
#Ruta raiz
@app.route('/')
def start():
    if 'loggedin' not in session:
        return redirect(url_for('inicio'))
    else:
	    return redirect(url_for('agendar'))

#Ruta pagina de inicio
@app.route('/inicio')
def inicio():
    if 'loggedin' not in session:
        return render_template("inicio.html")
    else:
        return redirect(url_for('agendar'))

#Ruta pagina de login y registro
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if 'loggedin' not in session:
        if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
            correo = request.form['login']
            contrasenia = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM usuario WHERE correo = % s AND contrasenia = % s', (correo, contrasenia, ))
            account = cursor.fetchone()
            if account:
                session['id'] = account['id']
                session['loggedin'] = True
                session['nombre'] = account['nombre']
                session['apellido'] = account['apellido']
                session['correo'] = account['correo']
                if account['tipo'] == 'Admin':
                    session['admin'] = True
                elif account['tipo'] == 'Doctor':
                    cursor.execute('SELECT id FROM doctor WHERE id_usuario = %s', (session['id'], ))
                    accountDoctor = cursor.fetchone()
                    session['idDoctor'] = accountDoctor['id']
                elif account['tipo'] == 'Secretario':
                    cursor.execute('SELECT id FROM secretario WHERE id_usuario = %s', (session['id'], ))
                    accountSecretario = cursor.fetchone()
                    session['idSecretario'] = accountSecretario['id']
                else:
                    session['idPaciente'] = session['id']
                return redirect(url_for('agendar'))
            else:
                msg = 'Usuario no existe.'
        elif request.method == 'POST' and 'nombre' in request.form and 'apellido-paterno' in request.form and 'apellido-materno' in request.form and 'sexo' in request.form and 'dia' in request.form and 'mes' in request.form and 'anio' in request.form and 'telefono' in request.form and 'correo_electronico_r' in request.form and 'domicilio' in request.form and 'passwordRegistro' in request.form:
            correo = request.form['correo_electronico_r']
            nombre = request.form['nombre']
            apellidos = request.form['apellido-paterno'] +" "+ request.form['apellido-materno']
            sexo = request.form['sexo']
            telefono = request.form['telefono']
            domicilio = request.form['domicilio']
            password = request.form['passwordRegistro']
            fechanacimiento = request.form['anio']+'-'+request.form['mes']+'-'+request.form['dia']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT correo FROM usuario WHERE correo = %s', (correo,))
            account = cursor.fetchone()
            if account:
                msg = 'Este correo ya esta registrado!'
            elif password_check(password) == False:
                msg = 'Contraseña no valida!'
            else:
                cursor.execute('INSERT INTO usuario (nombre, apellido, sexo, telefono, fecha_nacimiento, correo, domicilio, contrasenia, tipo) VALUES (% s, % s, % s, % s, % s, %s, %s, %s, %s)', (nombre, apellidos, sexo, telefono, fechanacimiento, correo, domicilio, password, 'Paciente', ))
                mysql.connection.commit()
                cursor.execute('SELECT id FROM usuario WHERE correo = %s', (correo,))
                account = cursor.fetchone()
                msg = 'Registro exitoso!'    
        return render_template('log_in.html', msg = msg)
    else:
        return redirect(url_for('agendar'))

#Ruta pagina de registro doctor
@app.route('/register/doc', methods =['GET', 'POST'])
def registro_doctor():
    msg = ''
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'admin' in session:
        if request.method == 'POST' and 'nombre' in request.form and 'apellido-paterno' in request.form and 'apellido-materno' in request.form and 'sexo' in request.form and 'dia' in request.form and 'mes' in request.form and 'anio' in request.form and 'telefono' in request.form and 'correo_electronico_r' in request.form and 'passwordRegistro' in request.form and 'cedula' in request.form:
            correo = request.form['correo_electronico_r']
            nombre = request.form['nombre']
            apellidos = request.form['apellido-paterno'] +" "+ request.form['apellido-materno']
            sexo = request.form['sexo']
            telefono = request.form['telefono']
            password = request.form['passwordRegistro']
            fechanacimiento = request.form['anio']+'-'+request.form['mes']+'-'+request.form['dia']
            cedula = request.form['cedula']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT correo FROM usuario WHERE correo = %s', (correo,))
            account = cursor.fetchone()
            if account:
                msg = 'Este correo ya esta registrado!'
            else:
                cursor.execute('INSERT INTO usuario (nombre, apellido, sexo, telefono, fecha_nacimiento, correo, contrasenia, tipo) VALUES (% s, % s, % s, % s, % s, %s, %s, %s)', (nombre, apellidos, sexo, telefono, fechanacimiento, correo, password, 'Doctor', ))
                mysql.connection.commit()
                cursor.execute('SELECT id FROM usuario WHERE correo = %s', (correo,))
                account = cursor.fetchone()
                cursor.execute('INSERT INTO doctor (id_usuario, cedula) VALUES (%s)', (account['id'],cedula,))
                msg = 'Registro exitoso!'    
        return render_template('registerDoc.html', msg = msg)
    else:
        return redirect(url_for('agendar'))
    
#Ruta pagina de registro secretario
@app.route('/register/sec', methods =['GET', 'POST'])
def registro_secretario():
    msg = ''
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idDoctor' in session:
        if request.method == 'POST' and 'nombre' in request.form and 'apellido-paterno' in request.form and 'apellido-materno' in request.form and 'sexo' in request.form and 'dia' in request.form and 'mes' in request.form and 'anio' in request.form and 'telefono' in request.form and 'correo_electronico_r' in request.form and 'passwordRegistro' in request.form:
            correo = request.form['correo_electronico_r']
            nombre = request.form['nombre']
            apellidos = request.form['apellido-paterno'] +" "+ request.form['apellido-materno']
            sexo = request.form['sexo']
            telefono = request.form['telefono']
            password = request.form['passwordRegistro']
            fechanacimiento = request.form['anio']+'-'+request.form['mes']+'-'+request.form['dia']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT correo FROM usuario WHERE correo = %s', (correo,))
            account = cursor.fetchone()
            if account:
                msg = 'Este correo ya esta registrado!'
            else:
                cursor.execute('INSERT INTO usuario (nombre, apellido, sexo, telefono, fecha_nacimiento, correo, contrasenia, tipo) VALUES (% s, % s, % s, % s, % s, %s, %s, %s)', (nombre, apellidos, sexo, telefono, fechanacimiento, correo, password, 'Secretario', ))
                mysql.connection.commit()
                cursor.execute('SELECT id FROM usuario WHERE correo = %s', (correo,))
                account = cursor.fetchone()
                cursor.execute('INSERT INTO secretario (id_usuario, id_doctor_afiliado) VALUES (%s)', (account['id'], session['idDoctor'],))
                msg = 'Registro exitoso!'    
        return render_template('registerSec.html', msg = msg)
    else:
        return redirect(url_for('agendar'))

#Ruta pagina de contactos
@app.route('/contacto', methods =['GET', 'POST'])
def contacto():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST' and 'nombre' in request.form and 'tipo' in request.form:
            nombre = request.form['nombre']
            tipo = request.form['tipo']
            cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND tipo = %s', (nombre, tipo,))
            contactos = cursor.fetchall()
        return render_template("contacto.html", contactos = contactos)
    
#Ruta pagina de contacto especifico
@app.route('/contacto/<id>')
def visualizacioncontacto(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute('SELECT * FROM usuario WHERE id = %s', (id,))
        contacto = cursor.fetchone()
        tipoContacto = contacto['tipo']
        if 'idPaciente' in session and tipoContacto == 'Paciente':
            abort(404)
        return render_template("contacto.html", contacto = contacto)

#Ruta pagina de informacion de perfil
@app.route('/perfil')
def perfil():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute('SELECT * FROM usuario WHERE id = %s', (session['id'],))
        perfil = cursor.fetchone()
        return render_template("perfil.html", perfil = perfil)

#Ruta pagina de edicion de informacion de perfil
@app.route('/perfil/editar', methods =['GET', 'POST'])
def editarperfil():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif request.method == 'POST' and 'nombre' in request.form and 'apellido' in request.form and 'sexo' in request.form and 'fecha_nacimiento' in request.form and 'telefono' in request.form and 'correo' in request.form and 'contrasenia' in request.form: 
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        sexo = request.form['sexo']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        correo = request.form['correo']
        contrasenia = request.form['contrasenia']
        if password_check(contrasenia) == False:
            msg = 'Contraseña no valida!'
        else:
            cursor.execute('UPDATE usuario SET nombre = %s, apellido = %s, sexo = %s, fecha_nacimiento = %s, telefono = %s, contrasenia = %s WHERE id = %s', (nombre, apellido, sexo, fecha_nacimiento, telefono, contrasenia, session['id'],))
            mysql.connection.commit()
            if 'idDoctor' in session and 'cedula' in request.form:
                cedula = request.form['cedula']
                cursor.execute('UPDATE doctor SET cedula = %s WHERE id = %s', (cedula, session['idDoctor'],))
                mysql.connection.commit()
            print('Datos actualizados!')
            session['nombre'] = nombre
            session['apellido'] = apellido
            session['correo'] = correo
    cursor.execute('SELECT * FROM usuario WHERE id = %s', (session['id'],))
    perfil = cursor.fetchone()
    return render_template("editarperfil.html", msg = msg, perfil = perfil)

#Ruta de pagina para agendar citas
@app.route('/citas/agendar', methods =['GET', 'POST'])
def agendar():
    msg = ''
    estado = 'En proceso'
    pacientes = ''
    doctores = ''
    id_doctor = ''
    id_paciente = ''
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        if 'idPaciente' in session:
            cursor.execute("SELECT * FROM DoctoresInformacionCompleta")
            doctores = cursor.fetchall()
            id_paciente = session['idPaciente']
            estado = 'Pendiente de revision'
        elif 'idDoctor' in session:
            cursor.execute("SELECT * FROM usuario WHERE tipo = 'Paciente'")
            id_doctor = session['idDoctor']
            pacientes = cursor.fetchall()
        elif 'admin' in session:
            cursor.execute("SELECT * FROM DoctoresInformacionCompleta")
            doctores = cursor.fetchall()
            cursor.execute("SELECT * FROM usuario WHERE tipo = 'Paciente'")
            pacientes = cursor.fetchall()
        if request.method == 'POST' and 'fecha' in request.form and 'hora' in request.form and 'motivo' in request.form:
            fecha_hora = request.form['fecha']+' '+request.form['hora']
            motivo = request.form['motivo']
            if 'id_doctor' in request.form:
                id_doctor = request.form['id_doctor']
            elif 'id_paciente' in request.form:
                id_paciente = request.form['id_paciente']
            cursor.execute('SELECT * FROM cita WHERE (id_doctor = %s OR id_paciente = %s) AND fecha_hora = %s',(id_doctor, id_paciente, fecha_hora,))
            existencia = cursor.fetchone()
            if existencia:
                msg = 'Ya hay una cita establecida en esa hora para el doctor y/o el paciente!'
            else:
                cursor.execute('INSERT INTO cita(id_doctor, id_paciente, fecha_hora, estado, motivo) VALUES (%s, %s, %s, %s, %s)', (id_doctor, id_paciente, fecha_hora, estado, motivo,))
                mysql.connection.commit()
                msg = 'Cita registrada con exito!'
        return render_template("agendar_cita_2.html", fecha_actual = fecha_actual, msg = msg, doctores = doctores, pacientes = pacientes)

#Ruta de pagina de visualizacion individual de cita
@app.route('/citas/<id>', methods =['GET', 'POST'])
def cita_individual(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    flag = False
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        if 'idPaciente' in session:
            cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_cita = %s AND id_paciente = %s',(id, session['idPaciente'],))
            cita = cursor.fetchone()
            if cita:
                flag = True
        elif 'idDoctor' in session:
            cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_cita = %s AND id_doctor = %s',(id, session['idDoctor'],))
            cita = cursor.fetchone()
            if cita:
                flag = True
        elif 'admin' in session:
            cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_cita = %s',(id,))
            cita = cursor.fetchone()
            if cita:
                flag = True
        if flag == False:
            abort(404)
    return render_template("cita.html", cita = cita)

#Ruta de pagina de edicion de cita
@app.route('/citas/<id>/editar', methods =['GET', 'POST'])
def edicion_cita(id):
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cita = ''
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idDoctor' in session:
        cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_cita = %s AND id_doctor = %s', (id,session['idDoctor'],))
        cita = cursor.fetchone()
        if not cita:
            abort(404)
    elif 'idPaciente' in session:
        cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_cita = %s AND id_paciente = %s', (id,session['idPaciente'],))
        cita = cursor.fetchone()
        if not cita:
            abort(404)
    elif 'admin' in session:
        cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_cita = %s)', (id,))
        cita = cursor.fetchone()
        if not cita:
            abort(404)
    if request.method == 'POST' and 'fecha' in request.form and 'hora' in request.form and 'motivo' in request.form:
        fecha_hora = request.form['fecha']+' '+request.form['hora']
        motivo = request.form['motivo']
        cursor.execute('SELECT * FROM cita WHERE (id_doctor = %s OR id_paciente = %s) AND fecha_hora = %s',(cita['id_doctor'], cita['id_paciente'], fecha_hora,))
        existencia = cursor.fetchone()
        if existencia:
            msg = 'Ya hay una cita establecida en esa hora para el doctor y/o el paciente!'
        else:
            cursor.execute('UPDATE cita SET fecha_hora = %s, estado = %s, motivo = %s WHERE id = %s', (fecha_hora, 'Pendiente de revision', motivo, id,))
            mysql.connection.commit()
            msg = 'Cita actualizada con exito!'
    return render_template("cita_editar.html", fecha_actual = fecha_actual, msg = msg, cita = cita)

#Ruta de agenda de citas
@app.route('/citas')
def citas():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idPaciente' in session:
        citasPendientes = citasPaciente(session['idPaciente'],'Pendiente de revision')
        citasVigentes = citasPaciente(session['idPaciente'],'En proceso')
        citasPasadas = citasPaciente(session['idPaciente'],'Terminada')
    elif 'idDoctor' in session:
        citasPendientes = citasDoctor(session['idDoctor'],'Pendiente de revision')
        citasVigentes = citasDoctor(session['idDoctor'],'En proceso')
        citasPasadas = citasDoctor(session['idDoctor'],'Terminada')
    elif 'idSecretario' in session:
        citasPendientes = citasSecretario(session['idSecretario'],'Pendiente de revision')
        citasVigentes = citasSecretario(session['idSecretario'],'En proceso')
        citasPasadas = citasSecretario(session['idSecretario'],'Terminada')
    elif 'admin' in session:
        if request.method == 'POST' and 'nombre' in request.form and 'tipo' in request.form:
            tipo = request.form['tipo']
            nombre = request.form['nombre']
            if tipo == 'Doctor':
                cursor.execute('SELECT id FROM doctor WHERE id_usuario = (SELECT id FROM usuario WHERE nombre = %s)', (nombre,))
                id = cursor.fetchone()
                citasPendientes = citasDoctor(id,'Pendiente de revision')
                citasVigentes = citasDoctor(id,'En proceso')
                citasPasadas = citasDoctor(id,'Terminada')
            elif tipo == 'Paciente':
                cursor.execute('SELECT id FROM usuario WHERE nombre = %s', (nombre,))
                id = cursor.fetchone()
                citasPendientes = citasPaciente(id,'Pendiente de revision')
                citasVigentes = citasPaciente(id,'En proceso')
                citasPasadas = citasPaciente(id,'Terminada')
            elif tipo == 'Secretario':
                cursor.execute('SELECT id FROM secretario WHERE id_usuario = (SELECT id FROM usuario WHERE nombre = %s)', (nombre,))
                id = cursor.fetchone()
                citasPendientes = citasSecretario(id,'Pendiente de revision')
                citasVigentes = citasSecretario(id,'En proceso')
                citasPasadas = citasSecretario(id,'Terminada')
    return render_template("citas.html", citasVigentes = citasVigentes, citasPendientes = citasPendientes, citasPasadas = citasPasadas)

def citasPaciente(id,estado):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cita WHERE id_paciente = %s AND estado = %s', (id, estado,))
    resultados = cursor.fetchall()
    return resultados

def citasDoctor(id,estado):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cita WHERE id_doctor = %s AND estado = %s', (id, estado,))
    resultados = cursor.fetchall()
    return resultados

def citasSecretario(id,estado):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cita WHERE id_secretario = %s AND estado = %s', (id, estado,))
    resultados = cursor.fetchall()
    return resultados

#Ruta de visualizacion general de expedientes
@app.route('/expedientes')
def expedientes():
    msg = ''
    expedientes = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idPaciente' in session:
        cursor.execute('SELECT * FROM ExpedientesInformacionCompleta WHERE id_paciente = %s', (session['id'],))
        expedientes = cursor.fetchall()
    elif 'idDoctor' in session:
        cursor.execute("SELECT * FROM ExpedientesInformacionCompleta WHERE id_doctor_creador = %s OR id_expediente = (SELECT id_expediente FROM permisos_expediente WHERE id_usuario = %s)", (session['idDoctor'],session['id'],))
        expedientes = cursor.fetchall()
    elif 'idSecretario' in session:
        cursor.execute("SELECT * FROM ExpedientesInformacionCompleta WHERE id_expediente = (SELECT id_expediente FROM permisos_expediente WHERE id_usuario = %s)", (session['id'],))
        expedientes = cursor.fetchall()
    elif 'admin' in session:
        cursor.execute("SELECT * FROM ExpedientesInformacionCompleta")
        expedientes = cursor.fetchall()
    if not expedientes:
        msg = 'No tienes ningun expediente registrado o autorizado!'
    return render_template('expedientes.html', expedientes = expedientes, msg = msg)

#Ruta de creacion de expediente
@app.route('/crearexpediente', methods =['GET', 'POST'])
def crearexpediente():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    id_paciente_seleccion = ''
    secretario = ''
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idDoctor' in session:
        if request.method == "POST" and 'info' in request.form and 'id_paciente_1' in request.form:
            id_paciente_seleccion = request.form['id_paciente_1']
            info = request.form['info']
            cursor.execute('SELECT * FROM expediente WHERE id_paciente = %s', (id_paciente_seleccion,))
            existencia = cursor.fetchone()
            if existencia:
                print('Este usuario ya tiene un expediente registrado!')
                msg = 'Este usuario ya tiene un expediente registrado!'
                return redirect(url_for('crearexpediente'))
            path = 'static/info/exp'
            with open(path+id_paciente_seleccion+'.txt', 'w') as f:
                f.write(str(info))
            cursor.execute('INSERT INTO expediente(id_paciente, id_doctor_creador, info) VALUES (%s, %s, %s)',(id_paciente_seleccion, session['idDoctor'], path+id_paciente_seleccion+'.txt',))
            mysql.connection.commit()
            cursor.execute('SELECT * FROM expediente WHERE id_paciente = %s',(id_paciente_seleccion,))
            id_expediente = cursor.fetchone()
            if 'pacienteShare' in request.form:
                cursor.execute('INSERT INTO permisos_expediente(id_expediente, id_usuario, tipo_permiso) VALUES (%s, %s, %s)', (id_expediente['id'], id_paciente_seleccion, 'VER',))
                mysql.connection.commit()
            if 'secretarioShare' in request.form:
                cursor.execute('INSERT INTO permisos_expediente(id_expediente, id_usuario, tipo_permiso) VALUES (%s, %s, %s)', (id_expediente['id'], request.form['secretarioShare'], 'VER',))
                mysql.connection.commit()
            if 'id_usuario_compartir' in request.form and 'privilegios' in request.form:
                id_usuario_compartir = request.form['id_usuario_compartir']
                privilegios = request.form['privilegios']
                cursor.execute('INSERT INTO permisos_expediente(id_expediente, id_usuario, tipo_permiso) VALUES (%s, %s, %s)', (id_expediente['id'], id_usuario_compartir, privilegios,))
            print('Expediente registrado con exito!')
            msg = 'Expediente registrado con exito!'
    else:
        abort(403)
    cursor.execute('SELECT DISTINCT usuario.id, usuario.nombre, usuario.apellido FROM usuario, cita WHERE usuario.id = cita.id_paciente AND id_doctor = %s',(session['idDoctor'],))
    pacientes = cursor.fetchall()
    cursor.execute("SELECT * FROM usuario WHERE tipo = 'Doctor' AND id <> %s",(session['id'],))
    usuarios = cursor.fetchall()
    cursor.execute("SELECT * FROM secretario WHERE id_doctor_afiliado = %s", (session['idDoctor'],))
    secretario = cursor.fetchone()
    if secretario:
        secretario = secretario
    else:
        secretario = ''
    return render_template('expediente_crear.html', pacientes = pacientes, msg = msg, secretario = secretario, usuarios = usuarios)

#Ruta de visualizacion individual de expediente
@app.route('/expediente/<id>')
def visualizacion_expediente(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    flag = False
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idPaciente' in session or 'idDoctor' in session or 'idSecretario' in session:
        cursor.execute('SELECT id_usuario FROM permisos_expediente WHERE id_expediente = %s AND id_usuario = %s', (id, session['id'],))
        permiso = cursor.fetchone()
        if 'idDoctor' in session:
            cursor.execute('SELECT id_paciente FROM expediente WHERE id = %s AND id_doctor_creador = %s', (id, session['idDoctor'],))
            creador = cursor.fetchone()
            if creador:
                flag = True
        if permiso:
            flag = True
        else:
            abort(404)
    if flag or 'admin' in session:
        cursor.execute('SELECT * FROM ExpedientesInformacionCompleta WHERE id_expediente = %s', (id,))
        expediente = cursor.fetchone()
        cursor.execute('SELECT * FROM CambiosInformacionCompleta WHERE id_expediente = %s ORDER BY id_cambio DESC', (id,))
        cambio_reciente = cursor.fetchone()
        f = open(expediente['info'], "r")
        contenido = f.read()
    return render_template('expediente_visualizacion.html', cambio_reciente = cambio_reciente, expediente = expediente, contenido = contenido)

#Ruta de cambios hechos al expediente
@app.route('/expediente/<id>/cambios')
def cambios_expediente(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    flag = False
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idPaciente' in session or 'idDoctor' in session or 'idSecretario' in session:
        cursor.execute('SELECT id_usuario FROM permisos_expediente WHERE id_expediente = %s AND id_usuario = %s', (id, session['id'],))
        permiso = cursor.fetchone()
        if(permiso):
            flag = True
        else:
            return redirect(url_for('expedientes'))
    if flag or 'admin' in session:
        cursor.execute('SELECT * FROM cambios WHERE id_expediente = %s', (id,))
        cambios = cursor.fetchall()
    return render_template('expediente_cambios.html', cambios = cambios)

#Ruta de edicion al expediente
@app.route('/expediente/<id>/editar', methods =['GET', 'POST'])
def editar_expediente(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    flag = False
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idPaciente' in session or 'idDoctor' in session or 'idSecretario' in session:
        cursor.execute("SELECT id_usuario FROM permisos_expediente WHERE id_expediente = %s AND id_usuario = %s AND tipo_permiso = 'EDITAR'", (id, session['id'],))
        permiso = cursor.fetchone()
        cursor.execute('SELECT id_paciente FROM expediente WHERE id = %s AND id_doctor_creador = %s', (id, session['idDoctor'],))
        creador = cursor.fetchone()
        if(permiso or creador):
            flag = True
        else:
            return redirect(url_for('expedientes'))
    if flag or 'admin' in session:
        cursor.execute('SELECT * FROM ExpedientesInformacionCompleta WHERE id_expediente = %s', (id,))
        expediente = cursor.fetchone()
        f = open(expediente['info'], "r")
        contenidoleer = f.read()
        if request.method == 'POST' and 'contenido' in request.form and 'notas' in request.form:
            contenidoescribir = request.form['contenido']
            notas = request.form['notas']
            path = 'static/info/exp'
            with open(path+str(expediente['id_paciente'])+'.txt', 'w') as f2:
                f2.write(str(contenidoescribir))
            cursor.execute('INSERT INTO cambios(id_expediente, id_doctor, info) VALUES (%s, %s, %s)', (id, session['idDoctor'], notas,))
            mysql.connection.commit()
            print('Cambio registrado con exito!')
            return redirect(url_for('expedientes'))
    return render_template('expediente_editar.html', expediente = expediente, contenido = contenidoleer)

#Ruta de pagina de error
@app.route('/error')
def Error():
    return render_template('error.html')

# Manejador de error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='Página no encontrada', description='Lo sentimos, la página que buscas no existe.'), 404

# Manejador de error 403
@app.errorhandler(403)
def access_forbidden(e):
    return render_template('error.html', error_code=403, error_message='Acceso denegado', description='No tienes permiso para acceder a esta página.'), 403

#Ruta de cerrar sesion
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('nombre', None)
    session.pop('apellido', None)
    session.pop('correo', None)
    session.pop('admin', None)
    session.pop('id', None)
    session.pop('idPaciente', None)
    session.pop('idDoctor', None)
    session.pop('idSecretario', None)
    return redirect(url_for('login'))

#@app.route('/login', methods =['GET', 'POST'])
#def login():
#	msg = ''
#	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#		nombreusuario = request.form['username']
#		contrasenia = request.form['password']
#		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#		cursor.execute('SELECT * FROM usuario WHERE username = % s AND contrasenia = % s', (nombreusuario, contrasenia, ))
#		account = cursor.fetchone()
#		if account:
#			session['loggedin'] = True
#			session['idUsuario'] = account['id']
#			session['nombre'] = account['nombre']
#			session['apellido'] = account['apellido']
#			session['nombreusuario'] = account['username']
#			session['correo'] = account['correo']
#			if(account['privilegio'] == 2):
#				session['admin'] = True
#			return redirect(url_for('home', msg=msg))
#		else:
#			msg = 'Nombre o contraseña incorrectos !'
#	return render_template('login.html', msg = msg)

#@app.route('/register', methods =['GET', 'POST'])
#def register():
#	msg = ''
#	if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'username' in request.form and 'mail' in request.form and 'password' in request.form:
#		nombre = request.form['firstname']
#		apellido = request.form['lastname']
#		nombreusuario = request.form['username']
#		correo = request.form['mail']
#		contrasenia = request.form['password']
#		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#		cursor.execute('SELECT * FROM usuario WHERE correo = % s', (correo, ))
#		account = cursor.fetchone()
#		if account:
#			msg = 'Este correo ya esta registrado !'
#		elif not re.match(r'[^@]+@[^@]+\.[^@]+', correo):
#			msg = 'Correo invalido !'
#		elif not re.match(r'[A-Za-z0-9]+', nombreusuario):
#			msg = 'El nombre de usuario solo debe contener letras y numeros !'
#		elif not re.match(r'[A-Za-z]+', nombre) or not re.match(r'[A-Za-z]+',apellido):
#			msg = 'El nombre y/o apellido solo debe contener letras !'
#		else:
#			cursor.execute('INSERT INTO usuario (nombre, apellido, username, correo, contrasenia) VALUES (% s, % s, % s, % s, % s)', (nombre, apellido, nombreusuario, correo, contrasenia, ))
#			mysql.connection.commit()
#			msg = 'Registro exitoso !'
#	return render_template('register.html', msg = msg)

#Funciones usuario admin


#Funciones usuario comun

if __name__ == '__main__':
    app.register_error_handler(404, page_not_found)
    app.run(debug=True)