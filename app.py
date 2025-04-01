from flask import Flask, render_template
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

    prueba1 = log(texto='Mensaje de prueba 1')
    prueba2 = log(texto='Mensaje de prueba 2')

    db.session.add(prueba1)
    db.session.add(prueba2)
    db.session.commit()


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
def agregar_mensaje_log(texto):
    mensajes_log.append(texto)

    #guardar el mensaje en la bd
    nuevo_registro = log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()




if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)