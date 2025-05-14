from flask import Flask,request , jsonify ,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json
app = Flask(__name__)
import re

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
TOKEN_GALAXIE = "LasG2ji3"

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
#Guardar log en la bd
                agregar_mensajes_log(json.dumps(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]
                        
                        enviar_mensajes_whatsapp(text,numero)
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)
#Guardar log en la bd
                    agregar_mensajes_log(json.dumps(messages))

        

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})


def enviar_mensajes_whatsapp(texto,number):
    texto_original = texto
    texto = texto.lower()

    if "Hola" in texto:
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

    elif re.match(r'^s\d+$', texto_original.strip(), re.IGNORECASE):
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "En un momento uno de nuestros agentes le estará contactando para brindarle información exacta."
            }
        }

    elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "text": {
                "preview_url": True,
                "body": "Claro aqui encontrarás nuestros productos! \n https://www.distribuidoragalaxie.com/kross"
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
                "body": "Cuéntanos, ¿En que productos estás interesado/a?"
            }
        }

    elif "3" in texto:
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

    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Por supuesto!, Brindame tu número de pedido."
            }
        }

    elif "5" in texto:
        
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

    
    # elif "6" in texto:
    #     data = {
    #         "messaging_product": "whatsapp",
    #         "recipient_type": "individual",
    #         "to": number,
    #         "type": "text",
    #         "text": {
    #             "preview_url": False,
    #             "body": "Horario de Atención : Lunes a Viernes. \n Horario : 9:00 am a 5:00 Pm \n Sabados \n Horario : 9:00 am a 12:00 pm"
    #         }
    #     }
    
    # elif "boton" in texto:
    #     data = {
    #         "messaging_product": "whatsapp",
    #         "recipient_type": "individual",
    #         "to": number,
    #         "type": "interactive",
    #         "interactive":{
    #             "type":"button",
    #             "body": {
    #                 "text": "¿ Confirmas tu registro?"
    #             },
    #             "footer": {
    #                 "text": "Selecciona una de las opciones"
    #             },
    #             "action": {
    #                 "buttons": [
    #                     {
    #                         "type": "reply",
    #                         "reply":{
    #                             "id":"btnsi",
    #                             "title":"Si"
    #                         }
    #                     },{
    #                         "type": "reply",
    #                         "reply":{
    #                             "id":"btnno",
    #                             "title":"No"
    #                         }
    #                     },{
    #                         "type": "reply",
    #                         "reply":{
    #                             "id":"btntalvez",
    #                             "title":"Talvez"
    #                         }
    #                     }
    #                 ]
    #             }
    #         }
           
    #         }
    # elif "btnsi" in texto:
    #     data = {
    #         "messaging_product": "whatsapp",
    #         "recipient_type": "individual",
    #         "to": number,
    #         "type": "text",
    #         "text": {
    #             "preview_url": False,
    #             "body": "Muchas Gracias por Aceptar."
    #         }
    #     }
    # elif "btnno" in texto:
    #     data = {
    #         "messaging_product": "whatsapp",
    #         "recipient_type": "individual",
    #         "to": number,
    #         "type": "text",
    #         "text": {
    #             "preview_url": False,
    #             "body": "Es una lastima."
    #         }
    #     }
    # elif "btntalvez" in texto:
    #     data = {
    #         "messaging_product": "whatsapp",
    #         "recipient_type": "individual",
    #         "to": number,
    #         "type": "text",
    #         "text": {
    #             "preview_url": False,
    #             "body": "Estaré a la espera."
    #         }
    #     }
    # elif "lista" in texto:
    #     data = {
    #         "messaging_product": "whatsapp",
    #         "recipient_type": "individual",
    #         "to": number,
    #         "type": "interactive",
    #         "interactive": {
    #             "type": "list",
    #             "body": {
    #                 "text": "Selecciona Alguna Opción"
    #             },"footer":{
    #                 "text": "Selecciona una de las opciones para poder ayudarte"
    #             },"action":{
    #                 "button": "Ver Opciones",
    #                 "secctions":[
    #                     {
    #                         "title": "Compra y Venta",
    #                         "rows": [
    #                             {
    #                                 "id":"btncompra",
    #                                 "title" : "Compra",
    #                                 "decription": "Compra los mejores articulos"
    #                             }, {
    #                                 "id":"btnvender",
    #                                 "title" : "Vender",
    #                                 "decription": "Vende lo que ya no estes usando"
    #                             }, 
    #                         ]
    #                     }, {
    #                         "title": "Distribución y Entrega",
    #                         "rows":[
    #                             {
    #                                 "id":"btndireccion",
    #                                 "title" : "Local",
    #                                 "decription": "Puedes visitar nuestro local."
    #                             }, {
    #                                 "id":"btnentrega",
    #                                 "title" : "Entrega",
    #                                 "decription": "Las entregas se realizan todos los dias."
    #                             }
    #                         ]
    #                     },
    #                 ]
    #             },
    #         }
    #     }

    
    else:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "1. Ver catálogo de productos \n 2. Solicitar cotización \n 3. Hablar con un asesor \n 4. Consultar estado de pedido \n 5. Donde está ubicados?"
            }
        }

    #convertir a json
    data=json.dumps(data)  


    headers = {
        "Content-Type" : "application/json",
        "Authorization": "Bearer EAAP7SbFV5BkBOZBZBPOxeFlwElSJoyxZAI5rJ43ZAprNW7uD4eZC43hmGX1ZCbSKyIdUOZBtODU88ZA3kJIEaAYaZCZCL78QcvDZAyTOjaGJsZAgKrPLgAyYxmRzvScqRtpRfPqPKw2J3tpwPTUXEcZCcpDhMn9EBu1ttfVUi1NE139wGZCcLMvjZCtK88u6sxAMOLUiV3n1AZDZD"
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
