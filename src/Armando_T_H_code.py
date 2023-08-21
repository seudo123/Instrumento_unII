from flask import Flask, jsonify, request
import re, bcrypt, mysql.connector

app = Flask(__name__)

# Conexion con la vase de de MYSQL WORKBENCH
conexion_config = {
    'host': 'localhost',#host donde se encuentra la base
    'user': 'root',#nombre de usuario de la base de datos
    'password': '27Oscar27',#contraseña
    'database': 'persona'#nombre de la base de datos
}
@app.route('/', methods=['GET'])
def ping():
    return jsonify({"response": "hello world"})

def get_db_connection():
    return mysql.connector.connect(**conexion_config)#Conexion

@app.route('/usuarios', methods=['GET'])
#Muesstra la lista de las credensiales de los usuarios que pueden acceder 
def get_usuarios():
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT correo, password FROM usuarios")
    result = cursor.fetchall()
    cursor.close()
    cnx.close()
    return jsonify(result), 200

@app.route('/login', methods=['POST'])

def add_usuarios():
    data = request.get_json()
#Revision de credenciales para acceder
    if 'correo' not in data:
        return {'error':'El correo es incorecto'}, 400

    if 'password' not in data or not es_password_valida(data['password']):
        return {'error':'La contraseña no es valida'}, 400

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT correo FROM usuarios WHERE correo = %s", (data['correo'],))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        cnx.close()
        return {'error':'Este usuario ya existe'}, 409#si se ingresa un usuario que ya aparese elsiguiente mensaje

    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    data['password'] = hashed_pw.decode('utf-8')
    cursor.execute("INSERT INTO usuarios (correo, password) VALUES (%s, %s)", (data['correo'], data['password']))
    cnx.commit()
    cursor.close()
    cnx.close()
    return {'success':'El acceso fue éxito'}, 201#En caso de poder accederestemensaje sera mostrado.

                        #Revision, ingresar, usuarios
@app.route('/dato_user/<int:usuario_id>', methods=['GET'])
def get_dato_user(usuario_id):
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dato_user WHERE usuario_id = %s", (usuario_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    if result:
        return jsonify(result), 200
    else:
        return {'error':'No se encontró el usuario'}, 404
#Metodo para ingresar usuarios 
@app.route('/dato_user', methods=['POST'])
def add_dato_user():
    data = request.get_json()
    required_fields = ['usuario_id', 'nombre', 'correo', 'estado_cv', 'codigopostal', 'edad', 'estado', 'ciudad']
    if not all(key in data for key in required_fields):
        return {'error': 'Faltan campos requeridos'}, 400

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)#compara los datos ingresados
    #los dato a comparar son los siguientes
    insert_query = """
        INSERT INTO dato_user (usuario_id, nombre, correo, estado_cv, codigopostal, edad, estado, ciudad)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (data['usuario_id'], data['nombre'], data['correo'], data['estado_cv'], data['codigopostal'], data['edad'], data['estado'], data['ciudad']))
    cnx.commit()
    cursor.close()
    cnx.close()

    return {'success':'Datos de usuario agregados con éxito'}, 201#los datos del empleo que tienen esta "guardado"

# Trabajo 

@app.route('/trabajo/<int:usuario_id>', methods=['GET'])#muestra los datos del trabajo
def get_trabajo(usuario_id):
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trabajo WHERE usuario_id = %s", (usuario_id,))#compara la id del usuario con su trabajo
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    if result:
        return jsonify(result), 200
    else:
        return {'error':'No se encontraron detalles de trabajo para el usuario'}, 404

@app.route('/trabajo', methods=['POST'])
def add_trabajo():
    data = request.get_json()
    #son los datos que se revisan antes de ingresar para guardar
    required_fields = ['usuario_id', 'trabaja', 'puesto', 'sueldo', 'dias_trabajo', 'horas_x_dia']
    if not all(key in data for key in required_fields):
        return {'error': 'Faltan campos requeridos'}, 400

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    #busca datos de los usuarios para ver las coinsidencias 
    insert_query = """
        INSERT INTO trabajo (usuario_id, trabaja, puesto, sueldo, dias_trabajo, horas_x_dia)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (data['usuario_id'], data['trabaja'], data['puesto'], data['sueldo'], data['dias_trabajo'], data['horas_x_dia']))
    cnx.commit()
    cursor.close()
    cnx.close()
    return {'success':'Datos de ocupasion agregados'}, 201

def es_password_valida(password):
    if len(password) < 8:#revisa que la contraseña sea mayor a 8 
        return False
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):#revisa los caracteresy ve que minimo tenga un dato de estos
        return False
    return True

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
