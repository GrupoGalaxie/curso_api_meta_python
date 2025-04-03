from flask import Flask,request , jsonify ,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
app = Flask(__name__)

#Configuracion de la base de datos sql lite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMT_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#modelo de la tabla log

class log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

#cREAR LA TABLA SI NO EXISTE

with app.app_context():
    db.create_all()

   


#Funcion para ordenar los registros por fecha y hora
def ordernar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
    #obtener todos los registros de la bd
    registros = log.query.all()
    registros_ordenados = ordernar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log = []


#funcion para agregar mensajes y guardar en la bd
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #guardar el mensaje en la bd
    nuevo_registro = log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()


#Token de verificacion para la configuracion
TOKEN_GALAXIE = "GALAXIE"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse


def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_GALAXIE:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401



def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        agregar_mensajes_log(json.dumps(objeto_mensaje))

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})

    



if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)