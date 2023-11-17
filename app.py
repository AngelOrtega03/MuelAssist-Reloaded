from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


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
        elif request.method == 'POST' and 'nombre' in request.form and 'apellido-paterno' in request.form and 'apellido-materno' in request.form and 'sexo' in request.form and 'dia' in request.form and 'mes' in request.form and 'anio' in request.form and 'telefono' in request.form and 'correo_electronico_r' in request.form and 'passwordRegistro' in request.form:
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
                cursor.execute('INSERT INTO usuario (nombre, apellido, sexo, telefono, fecha_nacimiento, correo, contrasenia, tipo) VALUES (% s, % s, % s, % s, % s, %s, %s, %s)', (nombre, apellidos, sexo, telefono, fechanacimiento, correo, password, 'Paciente', ))
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

#Ruta pagina de sucursales
@app.route('/sucursales')
def sucursales():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        return render_template("sucursales.html")

#Ruta pagina de contactos
@app.route('/contacto')
def contacto():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        return render_template("contacto.html")

#Ruta de agenda de citas
@app.route('/agendar')
def agendar():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    #elif 'idPaciente' in session or 'idDoctor' in session or 'admin' in session:
    #    if request.method == 'POST' and 'anio' in request.form and 'mes' in request.form and 'dia' in request.form and
    else:
        return render_template("agendar_citas.html")

#Ruta de visualizacion general de expedientes
@app.route('/expedientes')
def expedientes():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idPaciente' in session:
        cursor.execute('SELECT * FROM expediente WHERE id_paciente = %s', (session['id'],))
        expedientes = cursor.fetchall()
    elif 'idDoctor' in session:
        cursor.execute("SELECT * FROM expediente WHERE id_doctor_creador = %s OR id = (SELECT id_expediente FROM permisos_expediente WHERE id_usuario = %s)", (session['idDoctor'],session['id'],))
        expedientes = cursor.fetchall()
    elif 'idSecretario' in session:
        cursor.execute("SELECT * FROM expediente WHERE id = (SELECT id_expediente FROM permisos_expediente WHERE id_usuario = %s)", (session['id'],))
        expedientes = cursor.fetchall()
    elif 'admin' in session:
        cursor.execute("SELECT * FROM expediente")
        expedientes = cursor.fetchall()
    return render_template('expedientes.html', expedientes = expedientes)

#Ruta de creacion de expediente
@app.route('/crearexpediente', methods =['GET', 'POST'])
def crearexpediente():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idDoctor' in session:
        if request.method == "POST" and 'info' in request.form and 'tipo_sangre' in request.form and 'alergias' in request.form and 'paciente' in request.form:
            cursor.execute('SELECT id FROM usuario WHERE nombre = %s', (request.form['paciente']),)
            id_paciente = cursor.fetchone()
            info = request.form['info']
            tipo_sangre = request.form['tipo_sangre']
            alergias = request.form['alergias']
            cursor.execute('INSERT INTO expediente(id_paciente, id_doctor_creador, info, tipo_sangre, alergias) VALUES (%s, %s, %s, %s, %s)',(id_paciente, session['idDoctor'], info, tipo_sangre, alergias,))
            mysql.connection.commit()
            print('Expediente registrado con exito!')
            return redirect(url_for('expedientes'))
    cursor.execute('SELECT * FROM usuario WHERE id = (SELECT id_paciente FROM cita WHERE id_doctor = %s)',(session['idDoctor'],))
    pacientes = cursor.fetchall()
    return render_template('expedientes.html', pacientes = pacientes)

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
        if(permiso):
            flag = True
        else:
            return redirect(url_for('expedientes'))
    if flag or 'admin' in session:
        cursor.execute('SELECT * FROM expediente WHERE id = %s', (id,))
        expediente = cursor.fetchone()
    return render_template('expediente_visualizacion.html', expediente = expediente)

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
        if(permiso):
            flag = True
        else:
            return redirect(url_for('expedientes'))
    if flag or 'admin' in session:
        cursor.execute('SELECT * FROM expediente WHERE id = %s', (id,))
        expediente = cursor.fetchone()
        if request.method == 'POST' and 'info' in request.form and 'tipo_sangre' in request.form and 'alergias' in request.form and 'comentario' in request.form:
            info = request.form['info']
            tipo_sangre = request.form['tipo_sangre']
            alergias = request.form['alergias']
            comentario = request.form['comentario']
            cursor.execute('UPDATE expediente SET info = %s, tipo_sangre = %s, alergias = %s WHERE id = %s', (info, tipo_sangre, alergias, id,))
            mysql.connection.commit()
            cursor.execute('INSERT INTO cambios(id_expediente, id_doctor, info) VALUES (%s, %s, %s)', (id, session['idDoctor'], comentario,))
            mysql.connection.commit()
            print('Cambio registrado con exito!')
            return redirect(url_for('expedientes'))
    return render_template('expediente_editar.html', expediente = expediente)

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
    app.run(debug=True)