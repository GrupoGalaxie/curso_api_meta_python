from flask import Flask,request , jsonify ,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
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

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if  "type" in messages:
                tipo = messages["type"]

                if tipo == "interactive":
                    return 0
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)

        

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})


def enviar_mensajes_whatsapp(texto,number):
    texto = texto.lower()

    if "hola" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Hola Bienvenido, ¿Cómo estás?."
            }
        }
    elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "No creo que esta sea la mejor opcion, es guapo pero no tanto."
            }
        }

    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Esta es la mejor opcion ya que cuenta con una belleza superior a los demás."
            }
        }

    elif "3" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "8.984512369641095",
                "longitude": "-79.51576118170499",
                "name": "Edificio de Credicorp Bank",
                "address": "Calle 50"
            }
        }

    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "text": {
                "preview_url": True,
                "body": "Introducción a Kroos! https://youtu.be/9vOA5U7TDdo?si=G9M2vRLQAJ1GG20i"
            }
        }

    elif "5" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "En un momento unos de nuestros agentes se pondrá en contacto con usted."
            }
        }
    elif "6" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Horario de Atención : Lunes a Viernes. \n Horario : 9:00 am a 5:00 Pm \n Sabados \n Horario : 9:00 am a 12:00 pm"
            }
        }

    else:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "1. Cotizar con Carlos Cabarca \n 2. Cotizar con Marlos Alabarca \n 3. Cual es su ubicación? \n 4. Información General de la marca Kroos? \n 5. Hablar con un agente \n 6. Horario de atención"
            }
        }

    #convertir a json
    data=json.dumps(data)  


    headers = {
        "Content-Type" : "application/json",
        "Authorization": "Bearer EAAOlC6tsiBcBOZCZCLn5ZB6nl1fZCuvtO1j3V57EKqc4JhkXN8wZCJREitKawrDsBypzBzE45WcoCyrx4sRuQaOEAeS5CP6etK4A4GlMKZAaCl7xywJZBqgXP1MOZA8wgQfm5NLJZC1S7ij7yWqXEfoMhbAs9eCZC00wcrVM3OWeOt2YZBQn5YsXbipogIQ7WxJbZBQpBJZCO268faoVXsbsBgeIrZAxOk20VdkXS6UJRm2j4qWT8ZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v22.0/527257943810787/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason) 
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)