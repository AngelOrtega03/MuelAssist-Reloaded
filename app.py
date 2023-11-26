from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import pathlib
from assets.passcheck import password_check
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import secrets
import string
from flask import render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
#Update de librerias

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/img/usuarios/'

app.secret_key = 'your secret key'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Reemplaza con el servidor SMTP que estés utilizando
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'danygo243@gmail.com' # Reemplaza con tu correo electrónico
app.config['MAIL_PASSWORD'] = 'xywubtcoveneaeey'  # Reemplaza con tu contraseña
app.config['MAIL_DEFAULT_SENDER'] = 'danygo243@gmail.com'
mail = Mail(app)

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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE cita SET estado = 'Terminada' WHERE estado = 'En proceso' AND fecha_hora >= %s", (fecha_actual,))
    mysql.connection.commit()
    cursor.execute("SELECT * FROM usuario WHERE verificacion = 0 AND borrar = 'SI' AND fecha_peticion_borrar <= %s", (fecha_actual,))
    cuentas_a_borrar = cursor.fetchall()
    for cuenta in cuentas_a_borrar:
        send_account_deleted_email(cuenta['correo'])
    cursor.execute("UPDATE usuario SET verificacion = 1 WHERE borrar = 'SI' AND fecha_peticion_borrar <= %s", (fecha_actual,))
    mysql.connection.commit()
    if 'loggedin' not in session:
        return redirect(url_for('inicio'))
    else:
	    return redirect(url_for('inicio'))
    
#Ruta pagina de inicio
@app.route('/inicio')
def inicio():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM DoctoresInformacionCompleta')
    doctores = cursor.fetchall()
    return render_template("inicio.html", doctores = doctores)
    
# Ruta para activar la cuenta
@app.route('/activate/<code>')
def activate_account(code):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT correo FROM usuario WHERE codigo_activacion = %s', (code,))
    account = cursor.fetchone()

    if account:
        # Activa la cuenta en la base de datos (puedes realizar la actualización según tus necesidades)
        cursor.execute('UPDATE usuario SET activo = 1 WHERE correo = %s', (account['correo'],))
        mysql.connection.commit()

        # Redirige a una página de éxito o a donde prefieras
        return render_template('activation_success.html')
    else:
        # Redirige a una página de error si el código no es válido
        return render_template('activation_error.html')

# Ruta de registro
@app.route('/register', methods=['POST'])
def register():
    correo = request.form['correo']
    password = request.form['passwordRegistro']

    # Genera un código de activación único
    codigo_activacion = secrets.token_urlsafe(16)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO usuario (correo, contrasenia, codigo_activacion) VALUES (%s, %s, %s)',
                   (correo, password, codigo_activacion))
    mysql.connection.commit()

    # Envia el correo de activación
    send_activation_email(correo, codigo_activacion)

    # Redirige a una página de éxito
    return render_template('registration_success.html')

# Función para enviar el correo de activación
def send_activation_email(correo, codigo_activacion):
    activation_link = url_for('activate_account', code=codigo_activacion, _external=True)

    # Renderiza el contenido del archivo HTML
    email_content = render_template('activation_email.html',activation_link=activation_link)
    msg = Message('Activa tu cuenta', sender=('MuelAssist', ''), recipients=[correo])
    msg.html = email_content
    mail.send(msg)

# Función para enviar el correo de notificacion de cita
def send_appointment_email(correo, cita):
    subject = 'Tienes una cita agendada'
    sender = 'tu_correo@example.com'
    recipients = [correo]

    # Renderiza el contenido del archivo HTML
    email_content = render_template('appointment_email.html', cita=cita)

    msg = Message(subject, sender = ('MuelAssist', ''), recipients=recipients)
    msg.html = email_content
    mail.send(msg)

# Función para enviar el correo de notificacion de modificacion de cita
def send_appointment_edit_email(correo, cita):
    subject = 'Tu cita a sido modificada con exito'
    sender = 'tu_correo@example.com'
    recipients = [correo]

    # Renderiza el contenido del archivo HTML
    email_content = render_template('appointment_edit_email.html', cita=cita)

    msg = Message(subject, sender=('MuelAssist', ''), recipients=recipients)
    msg.html = email_content
    mail.send(msg)

# Función para enviar el correo de notificacion de proceso de eliminacion de cuenta
def send_account_cancel_email(correo, cuenta):
    subject = f'Tu cuenta se borrará el {cuenta["fecha_peticion_borrar"]}'
    sender = ('MuelAssist', 'tu_correo@example.com')
    recipients = [correo]

    # Renderiza el contenido del archivo HTML
    email_content = render_template('account_cancel_email.html', cuenta=cuenta)

    msg = Message(subject, sender=('MuelAssist',''), recipients=recipients)
    msg.html = email_content
    mail.send(msg)

# Función para enviar el correo de notificacion de eliminacion de cuenta
def send_account_deleted_email(correo):
    subject = 'Tu cuenta ha sido borrada'
    sender = ('MuelAssist', 'tu_correo@example.com')
    recipients = [correo]

    # Renderiza el contenido del archivo HTML
    email_content = render_template('account_deleted_email.html')

    msg = Message(subject, sender=('MuelAssist',''), recipients=recipients)
    msg.html = email_content
    mail.send(msg)

#Ruta pagina de login y registro
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if 'loggedin' not in session:
        try:
            if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
                correo = request.form['login']
                contrasenia = request.form['password']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM usuario WHERE correo = % s AND verificacion = 0', (correo, ))
                account = cursor.fetchone()

                if check_password_hash(account['contrasenia'],contrasenia) == True:
                    if account['activo'] == 1:
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

                        return redirect(url_for('inicio'))
                    else:
                        msg = 'CUENTA NO ACTIVADA. Por favor, revise su correo para activar su cuenta.'
                else:
                    msg = 'Usuario no existe o contraseña incorrecta.'

            elif request.method == 'POST' and 'nombre' in request.form and 'apellido-paterno' in request.form and 'apellido-materno' in request.form and 'sexo' in request.form and 'dob' in request.form and 'telefono' in request.form and 'correo_electronico_r' in request.form and 'domicilio' in request.form and 'passwordRegistro' in request.form and 'tipo_sangre' in request.form:
                correo = request.form['correo_electronico_r']
                nombre = request.form['nombre']
                apellidos = request.form['apellido-paterno'] +" "+ request.form['apellido-materno']
                sexo = request.form['sexo']
                telefono = request.form['telefono']
                domicilio = request.form['domicilio']
                password = request.form['passwordRegistro']
                fechanacimiento = request.form['dob']
                tipo_sangre = request.form['tipo_sangre']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT correo FROM usuario WHERE correo = %s', (correo,))
                account = cursor.fetchone()
                if account:
                    msg = 'Este correo ya esta registrado!'
                elif password_check(password) == False:
                    msg = 'Contraseña no valida!'
                else:
                    # Genera un hash en la contraseña
                    contraseña_hasheada = generate_password_hash(password, 'pbkdf2')

                    # Genera un código de activación único
                    codigo_activacion = secrets.token_urlsafe(16)

                    cursor.execute('INSERT INTO usuario (nombre, apellido, sexo, telefono, fecha_nacimiento, correo, domicilio, contrasenia, tipo, tipo_sangre, codigo_activacion) VALUES (% s, % s, % s, % s, % s, %s, %s, %s, %s, %s, %s)', (nombre, apellidos, sexo, telefono, fechanacimiento, correo, domicilio, contraseña_hasheada, 'Paciente', tipo_sangre, codigo_activacion,))

                    # Envía un correo de activación al usuario
                    send_activation_email(correo, codigo_activacion)
                    mysql.connection.commit()

                    cursor.execute('SELECT id FROM usuario WHERE correo = %s', (correo,))
                    account = cursor.fetchone()
                    msg = 'Registro exitoso, Se ha enviado un correo de activación a tu dirección de correo electronico registrada.'

        except Exception as e:
            print(f"Error en el proceso de inicio de sesión o registro: {e}")
            msg = 'Error en el proceso de inicio de sesión o registro. Por favor, inténtelo nuevamente.'   
        
        return render_template('log_in.html', msg = msg)
    else:
        return redirect(url_for('inicio'))
    
# Ruta para enviar el correo electrónico de restablecimiento de contraseña
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE correo = %s', (email,))
        user = cursor.fetchone()
        if user:
            # Envía el correo electrónico de restablecimiento de contraseña
            send_password_reset_email(email)
            flash('Revisa tu correo electrónico y sigue las instrucciones para restablecer tu contraseña.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Correo no registrado.', 'danger')

    return render_template('reset_pass_request.html')

# Configura la conexión a la base de datos (ajusta según tus credenciales y configuración)
#db = MySQLdb.connect(host="146.190.218.21", user="muelitas", passwd="CONTRASENIAENMINUSCULAS", db="muelassist_sql")

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'reset_token' in session and 'reset_email' in session:
        if token == session['reset_token']:
            if request.method == 'POST':
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']

                if new_password == confirm_password and password_check(new_password) == True:

                    # Obtiene el usuario basado en el correo electrónico almacenado en la sesión
                    cursor.execute('SELECT * FROM usuario WHERE correo = %s', (session['reset_email'],))
                    user_data = cursor.fetchone()

                    if user_data:
                        #Encripta la contraseña
                        contraseña_hasheada = generate_password_hash(new_password, 'pbkdf2')

                        # Actualiza la contraseña del usuario en la base de datos
                        cursor.execute('UPDATE usuario SET contrasenia = %s WHERE correo = %s', (contraseña_hasheada, session['reset_email']))
                        mysql.connection.commit()
                        
                        flash('Tu contraseña se ha restablecido correctamente.', 'success')
                        session.pop('reset_token', None)
                        session.pop('reset_email', None)
                        return redirect(url_for('login'))
                    else:
                        flash('Usuario no encontrado.', 'danger')
                else:
                    flash('Las contraseñas no coinciden y/o no estan bajo los limites establecidos.', 'danger')

            return render_template('reset_password.html', token=token)
        else:
            flash('Token de restablecimiento no válido o caducado.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Token de restablecimiento no válido o caducado.', 'danger')
        return redirect(url_for('login'))



# Función para enviar el correo electrónico de restablecimiento de contraseña
def send_password_reset_email(user_email):
    token = secrets.token_urlsafe(20)
    session['reset_token'] = token
    session['reset_email'] = user_email

    reset_url = url_for('reset_password', token=token, _external=True)

    msg = Message('Solicitud de restablecimiento de contraseña', 
                  sender=('MuelAssist', ''), 
                  recipients=[user_email])

    # Utiliza render_template_string para cargar el contenido del archivo HTML
    msg.html = render_template('reset_password_email.html', reset_url=reset_url)
    mail.send(msg)

#Ruta pagina de registro doctor
@app.route('/register/doc', methods =['GET', 'POST'])
def registro_doctor():
    msg = ''
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'admin' in session:
        if request.method == 'POST' and 'nombre' in request.form and 'apellido-paterno' in request.form and 'apellido-materno' in request.form and 'sexo' in request.form and 'dob' in request.form and 'telefono' in request.form and 'correo_electronico_r' in request.form and 'passwordRegistro' in request.form and 'cedula' in request.form and 'domicilio' in request.form and 'rfc' in request.form and 'curp' in request.form and 'exp_lab' in request.form and 'ref_lab' in request.form and 'tipo_sangre' in request.form:
            correo = request.form['correo_electronico_r']
            nombre = request.form['nombre']
            apellidos = request.form['apellido-paterno'] +" "+ request.form['apellido-materno']
            sexo = request.form['sexo']
            telefono = request.form['telefono']
            password = request.form['passwordRegistro']
            fechanacimiento = request.form['dob']
            domicilio = request.form['domicilio']
            cedula = request.form['cedula']
            rfc = request.form['rfc']
            curp = request.form['curp']
            tipo_sangre = request.form['tipo_sangre']
            experiencia_laboral = request.form['exp_lab']
            referencia_laboral = request.form['ref_lab']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT id,correo FROM usuario WHERE correo = %s', (correo,))
            account = cursor.fetchone()
            if account:
                msg = 'Este correo ya esta registrado!'
            elif password_check(password) == False:
                msg = 'Contraseña no valida!'
            else:
                #Encripta la contraseña
                contraseña_hasheada = generate_password_hash(password, 'pbkdf2')

                # Genera un código de activación único
                codigo_activacion = secrets.token_urlsafe(16)

                cursor.execute('INSERT INTO usuario (nombre, apellido, sexo, telefono, fecha_nacimiento, correo, domicilio, contrasenia, tipo, tipo_sangre, codigo_activacion) VALUES (% s, % s, % s, % s, % s, %s, %s, %s, %s, %s, %s)', (nombre, apellidos, sexo, telefono, fechanacimiento, correo, domicilio, contraseña_hasheada, 'Doctor', tipo_sangre, codigo_activacion,))

                # Envía un correo de activación al usuario
                send_activation_email(correo, codigo_activacion)
                mysql.connection.commit()

                cursor.execute('SELECT id FROM usuario WHERE correo = %s', (correo,))
                account2 = cursor.fetchone()
                path = 'static/info/lab'
                with open(path+'exp'+str(account2['id'])+'.txt', 'w') as f:
                    f.write(str(experiencia_laboral))
                with open(path+'ref'+str(account2['id'])+'.txt', 'w') as f:
                    f.write(str(referencia_laboral))
                print(account2['id'])
                cursor.execute('INSERT INTO doctor (id_usuario, cedula, rfc, curp, experiencia_laboral, referencia_laboral) VALUES (%s, %s, %s, %s, %s, %s)', (account2['id'],cedula,rfc,curp,path+'exp'+str(account2['id'])+'.txt', path+'ref'+str(account2['id'])+'.txt',))
                mysql.connection.commit()
                msg = 'Registro exitoso! Se ha enviado un correo de activación a tu dirección.'   
        return render_template('registerDoc.html', msg = msg)
    else:
        abort(403)
    
#Ruta pagina de registro secretario
@app.route('/register/sec', methods =['GET', 'POST'])
def registro_secretario():
    msg = ''
    id_doctor_afiliado = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif 'idDoctor' in session or 'admin' in session:
        if request.method == 'POST' and 'nombre' in request.form and 'apellido-paterno' in request.form and 'apellido-materno' in request.form and 'sexo' in request.form and 'dob' in request.form and 'telefono' in request.form and 'correo_electronico_r' in request.form and 'passwordRegistro' in request.form and 'domicilio' in request.form and 'rfc' in request.form and 'curp' in request.form and 'tipo_sangre' in request.form and 'exp_lab' in request.form and 'ref_lab' in request.form:
            if 'idDoctor' in session:
                id_doctor_afiliado = session['idDoctor']
            elif 'doctor' in request.form:
                id_doctor_afiliado = request.form['doctor']
            correo = request.form['correo_electronico_r']
            nombre = request.form['nombre']
            apellidos = request.form['apellido-paterno'] +" "+ request.form['apellido-materno']
            sexo = request.form['sexo']
            telefono = request.form['telefono']
            password = request.form['passwordRegistro']
            fechanacimiento = request.form['dob']
            tipo_sangre = request.form['tipo_sangre']
            domicilio = request.form['domicilio']
            rfc = request.form['rfc']
            curp = request.form['curp']
            exp_lab = request.form['exp_lab']
            ref_lab = request.form['ref_lab']
            cursor.execute('SELECT correo FROM usuario WHERE correo = %s', (correo,))
            account = cursor.fetchone()
            if account:
                msg = 'Este correo ya esta registrado!'
            elif password_check(password) == False:
                msg = 'Contraseña no valida!'
            else:
                #Encripta la contraseña
                contraseña_hasheada = generate_password_hash(password, 'pbkdf2')

                # Genera un código de activación único
                codigo_activacion = secrets.token_urlsafe(16)

                cursor.execute('INSERT INTO usuario (nombre, apellido, sexo, telefono, fecha_nacimiento, correo, contrasenia, tipo, tipo_sangre, domicilio, codigo_activacion) VALUES (% s, % s, % s, % s, % s, %s, %s, %s, %s, %s, %s)', (nombre, apellidos, sexo, telefono, fechanacimiento, correo, contraseña_hasheada, 'Secretario', tipo_sangre, domicilio, codigo_activacion,))
                
                # Envía un correo de activación al usuario
                send_activation_email(correo, codigo_activacion)
                mysql.connection.commit()

                cursor.execute('SELECT id FROM usuario WHERE correo = %s', (correo,))
                account = cursor.fetchone()
                path = 'static/info/lab'
                with open(path+'exp'+str(account['id'])+'.txt', 'w') as f1:
                    f1.write(str(exp_lab))
                with open(path+'ref'+str(account['id'])+'.txt', 'w') as f2:
                    f2.write(str(ref_lab))
                print(account['id'])
                cursor.execute('INSERT INTO secretario (id_usuario, id_doctor_afiliado, rfc, curp, experiencia_laboral, referencia_laboral) VALUES (%s, %s, %s, %s, %s, %s)', (account['id'], id_doctor_afiliado, rfc, curp, path+'exp'+str(account['id'])+'.txt', path+'ref'+str(account['id'])+'.txt',))
                mysql.connection.commit()
                msg = 'Registro exitoso! Se ha enviado un correo de activación a tu dirección.'
        cursor.execute('SELECT * FROM DoctoresInformacionCompleta')
        doctores = cursor.fetchall()    
        return render_template('registerSec.html', msg = msg, doctores = doctores)
    else:
        return redirect(url_for('inicio'))

#Ruta pagina de contactos
@app.route('/contacto', methods =['GET', 'POST'])
def contacto():
    msg = ''
    contactos = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST' and 'Busqueda' in request.form and 'tipo' in request.form:
            busqueda = request.form['Busqueda']
            tipo = request.form['tipo']
            if 'admin' in session or 'idDoctor' in session or 'idSecretario' in session:
                if tipo == 'nombre':
                    cursor.execute("SELECT * FROM usuario WHERE nombre = %s AND verificacion = 0", (busqueda,))
                elif tipo == 'id':
                    cursor.execute("SELECT * FROM usuario WHERE id = %s AND verificacion = 0", (busqueda,))
                elif tipo == 'correo':
                    cursor.execute("SELECT * FROM usuario WHERE correo = %s AND verificacion = 0", (busqueda,))
                elif tipo == 'telefono':
                    cursor.execute("SELECT * FROM usuario WHERE telefono = %s AND verificacion = 0", (busqueda,))
            else:
                if tipo == 'nombre':
                    cursor.execute("SELECT * FROM usuario WHERE nombre = %s AND verificacion = 0 AND tipo <> 'Paciente'", (busqueda,))
                elif tipo == 'id':
                    cursor.execute("SELECT * FROM usuario WHERE id = %s AND verificacion = 0 AND tipo <> 'Paciente'", (busqueda,))
                elif tipo == 'correo':
                    cursor.execute("SELECT * FROM usuario WHERE correo = %s AND verificacion = 0 AND tipo <> 'Paciente'", (busqueda,))
                elif tipo == 'telefono':
                    cursor.execute("SELECT * FROM usuario WHERE telefono = %s AND verificacion = 0 AND tipo <> 'Paciente'", (busqueda,))
            contactos = cursor.fetchall()
            if not contactos:
                msg = "No se encontró el contacto"
        return render_template("contacto.html", contactos = contactos, msg = msg)
    
#Ruta pagina de contacto especifico
@app.route('/contacto/<id>')
def visualizacioncontacto(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    datos_extra = ''
    exp_lab = ''
    ref_lab = ''
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute('SELECT * FROM usuario WHERE id = %s AND verificacion = 0', (id,))
        contacto = cursor.fetchone()
        if contacto:
            tipoContacto = contacto['tipo']
            if 'idPaciente' in session and tipoContacto == 'Paciente':
                abort(404)
            elif tipoContacto == 'Doctor' or tipoContacto == 'Secretario':
                if tipoContacto == 'Doctor':
                    cursor.execute('SELECT * FROM doctor WHERE id_usuario = %s', (id,))
                elif tipoContacto == 'Secretario':
                    cursor.execute('SELECT * FROM SecretariosInformacionCompleta WHERE id_usuario = %s', (id,))
                datos_extra = cursor.fetchone()
                try:
                    f1 = open('static/info/labexp'+str(id)+'.txt', "r")
                    exp_lab = f1.read()
                    f2 = open('static/info/labref'+str(id)+'.txt', "r")
                    ref_lab = f2.read()
                except Exception as e:
                    print(f"No hay registros de tanto experiencias o referencias laborales: {e}")
                    exp_lab = ''
                    ref_lab = ''
        else:
            abort(404)
        return render_template("contacto_visualizacion.html", contacto = contacto, datos_extra = datos_extra, exp_lab = exp_lab, ref_lab = ref_lab)

#Ruta pagina de informacion de perfil
@app.route('/perfil', methods =['GET', 'POST'])
def perfil():
    msg = ''
    exp_lab = ''
    ref_lab = ''
    datos_extra = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        cursor.execute('SELECT * FROM usuario WHERE id = %s', (session['id'],))
        perfil = cursor.fetchone()
        if 'idDoctor' in session or 'idSecretario' in session:
            if 'idDoctor':
                cursor.execute('SELECT * FROM doctor WHERE id_usuario = %s', (session['id'],))
            elif 'idSecretario':
                cursor.execute('SELECT * FROM SecretariosInformacionCompleta WHERE id_usuario = %s', (session['id'],))
            datos_extra = cursor.fetchone()
            f1 = open('static/info/labexp'+str(session['id'])+'.txt', "r")
            exp_lab = f1.read()
            f2 = open('static/info/labref'+str(session['id'])+'.txt', "r")
            ref_lab = f2.read()
        if request.method == 'POST' and 'cancelar' in request.form:
            fecha_actual = datetime.now() + timedelta(hours=24)
            fecha_borrar = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE usuario SET borrar = 'SI', fecha_peticion_borrar = %s WHERE id = %s", (fecha_borrar,session['id'],))
            mysql.connection.commit()
            send_account_cancel_email(session['correo'], perfil)
            msg = 'Tu perfil se borrara en la fecha '+fecha_borrar
        elif request.method == 'POST' and 'reactivar' in request.form:
            cursor.execute("UPDATE usuario SET borrar = 'NO', fecha_peticion_borrar = '0000-00-00 00:00:00' WHERE id = %s", (session['id'],))
            mysql.connection.commit()
            msg = 'Tu perfil se reactivo'
        return render_template("perfil.html", msg = msg, perfil = perfil, exp_lab = exp_lab, ref_lab = ref_lab, datos_extra = datos_extra)

#Ruta pagina de edicion de informacion de perfil
@app.route('/perfil/editar', methods =['GET', 'POST'])
def editarperfil():
    msg = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif request.method == 'POST': 
        nombre = request.form['nombre']
        apellido = request.form['apellidos']
        domicilio = request.form['domicilio']
        telefono = request.form['telefono']
        correo = request.form['correo']
        contrasenia = request.form['contrasenia']
        if password_check(contrasenia) == False:
            msg = 'Contraseña no valida!'
        else:
            if 'file1' in request.files:
                print('Imagen encontrada...')
                imagen = request.files['file1']
                file_name = generate_custom_name(imagen.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                print(path)
                imagen.save(path)
                cursor.execute('UPDATE usuario SET imagen_perfil = %s WHERE id = %s', (path, session['id'],))
                mysql.connection.commit()
            # Genera un hash en la contraseña
            contraseña_hasheada = generate_password_hash(contrasenia, 'pbkdf2')

            cursor.execute('UPDATE usuario SET nombre = %s, apellido = %s, domicilio = %s, telefono = %s, correo = %s, contrasenia = %s WHERE id = %s', (nombre, apellido, domicilio, telefono, correo, contraseña_hasheada, session['id'],))
            mysql.connection.commit()
            print('Datos actualizados!')
            msg = 'Datos actualizados!'
            session['nombre'] = nombre
            session['apellido'] = apellido
            session['correo'] = correo
    cursor.execute('SELECT * FROM usuario WHERE id = %s', (session['id'],))
    perfil = cursor.fetchone()
    return render_template("editarperfil.html", msg = msg, perfil = perfil)

#Funcion que genera nombre para imagen subida
def generate_custom_name(original_file_name):
    return "user" +str(session['id'])+pathlib.Path(original_file_name).suffix

#Funcion que genera nombre para imagen subida de expediente
def generate_custom_name_exp(original_file_name, idExpediente):
    return "expimg" +str(idExpediente)+pathlib.Path(original_file_name).suffix

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
                cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_doctor = %s AND id_paciente = %s AND fecha_hora = %s', (id_doctor, id_paciente, fecha_hora,))
                cita = cursor.fetchone()
                send_appointment_email(cita['correo_doctor'], cita)
                send_appointment_email(cita['correo_paciente'], cita)
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
    estado = ''
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
            if 'estado' in request.form:
                estado = request.form['estado']
                cursor.execute('UPDATE cita SET fecha_hora = %s, estado = %s, motivo = %s, estado = %s WHERE id = %s', (fecha_hora, 'Pendiente de revision', motivo, estado, id,))
            else:
                cursor.execute('UPDATE cita SET fecha_hora = %s, estado = %s, motivo = %s WHERE id = %s', (fecha_hora, 'Pendiente de revision', motivo, id,))
            mysql.connection.commit()
            msg = 'Cita actualizada con exito!'
            cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_cita = %s', (id,))
            cita = cursor.fetchone()
            send_appointment_edit_email(cita['correo_doctor'], cita)
            send_appointment_edit_email(cita['correo_paciente'], cita)
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
    cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_paciente = %s AND estado = %s', (id, estado,))
    resultados = cursor.fetchall()
    return resultados

def citasDoctor(id,estado):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_doctor = %s AND estado = %s', (id, estado,))
    resultados = cursor.fetchall()
    return resultados

def citasSecretario(id,estado):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM CitaInformacionCompleta WHERE id_secretario = %s AND estado = %s', (id, estado,))
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
        if request.method == "POST" and 'info' in request.form and 'id_paciente_1' in request.form and 'observaciones' in request.form:
            id_paciente_seleccion = request.form['id_paciente_1']
            info = request.form['info']
            observaciones = request.form['observaciones']
            cursor.execute('SELECT * FROM expediente WHERE id_paciente = %s', (id_paciente_seleccion,))
            existencia = cursor.fetchone()
            if existencia:
                print('Este usuario ya tiene un expediente registrado!')
                msg = 'Este usuario ya tiene un expediente registrado!'
                return redirect(url_for('crearexpediente'))
            path1 = 'static/info/exp'
            with open(path1+id_paciente_seleccion+'.txt', 'w') as f:
                f.write(str(info))
            path2 = 'static/info/obs'
            with open(path2+id_paciente_seleccion+'.txt', 'w') as f:
                f.write(str(observaciones))
            cursor.execute('INSERT INTO expediente(id_paciente, id_doctor_creador, info, observacion) VALUES (%s, %s, %s, %s)',(id_paciente_seleccion, session['idDoctor'], path1+id_paciente_seleccion+'.txt', path2+id_paciente_seleccion+'.txt',))
            mysql.connection.commit()
            cursor.execute('SELECT * FROM expediente WHERE id_paciente = %s',(id_paciente_seleccion,))
            id_expediente = cursor.fetchone()
            if 'archivo' in request.files:
                print('Imagen encontrada...')
                imagen = request.files['archivo']
                file_name = generate_custom_name_exp(imagen.filename, id_expediente['id'])
                path = os.path.join("static/img/expediente/", file_name)
                print(path)
                imagen.save(path)
                cursor.execute('UPDATE expediente SET imagen = %s WHERE id = %s', (path, id_expediente['id'],))
                mysql.connection.commit()
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
        if flag == False:
            abort(404)
    if flag or 'admin' in session:
        cursor.execute('SELECT * FROM ExpedientesInformacionCompleta WHERE id_expediente = %s', (id,))
        expediente = cursor.fetchone()
        cursor.execute('SELECT * FROM CambiosInformacionCompleta WHERE id_expediente = %s ORDER BY id_cambio DESC', (id,))
        cambio_reciente = cursor.fetchone()
        f = open(expediente['info'], "r")
        contenido = f.read()
        f = open(expediente['observacion'], "r")
        observacion = f.read()
    return render_template('expediente_visualizacion.html', cambio_reciente = cambio_reciente, expediente = expediente, contenido = contenido, observacion = observacion)

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
        f = open(expediente['observacion'], "r")
        observacionleer = f.read()
        if request.method == 'POST' and 'contenido' in request.form and 'observaciones' in request.form and 'notas' in request.form:
            contenidoescribir = request.form['contenido']
            observacionesescribir = request.form['observaciones']
            notas = request.form['notas']
            path1 = 'static/info/exp'
            with open(path1+str(expediente['id_paciente'])+'.txt', 'w') as f2:
                f2.write(str(contenidoescribir))
            path2 = 'static/info/obs'
            with open(path2+str(expediente['id_paciente'])+'.txt', 'w') as f3:
                f3.write(str(observacionesescribir))
            if 'archivo' in request.files:
                print('Imagen encontrada...')
                imagen = request.files['archivo']
                file_name = generate_custom_name_exp(imagen.filename, id)
                path = os.path.join("static/img/expediente/", file_name)
                print(path)
                imagen.save(path)
            cursor.execute('INSERT INTO cambios(id_expediente, id_doctor, info) VALUES (%s, %s, %s)', (id, session['idDoctor'], notas,))
            mysql.connection.commit()
            print('Cambio registrado con exito!')
            return redirect(url_for('expedientes'))
    return render_template('expediente_editar.html', expediente = expediente, contenido = contenidoleer, observacion = observacionleer)

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
    return redirect(url_for('inicio'))

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
