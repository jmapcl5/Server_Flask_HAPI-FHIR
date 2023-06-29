from flask import Flask, render_template, request , redirect, jsonify , url_for
from config import config
from flask_mqtt import Mqtt
from threading import Lock
import paho.mqtt.   client as mqtt
from flask_socketio import SocketIO , send
import requests 
import sys
import plotly.graph_objects as go
import time
import datetime
import json

#from fhirclient import client
#from fhirclient.models.patient import Patient
nombre = ''

app=Flask(__name__)


FHIR_SERVER_URL = 'http://localhost:8080/fhir'

#---------variables usadas------------------------#
data_list=[]
valor_updated = ""
temperatura = 0
humedad = 0
time_list=[]
temp_list=[]
time_list2=[]
id = 0
datos= []
#-------------------------------------------------#
#-------------MQTT-----------------------------#
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['MQTT_BROKER_URL'] = '172.20.10.4'  # Cambiar por la dirección IP o nombre de dominio de tu broker MQTT
app.config['MQTT_BROKER_PORT'] = 1883  # Puerto MQTT por defecto
app.config['MQTT_USERNAME'] = 'jmapcl185'  # Cambiar por tu nombre de usuario MQTT
app.config['MQTT_PASSWORD'] = '12345'  # Cambiar por tu contraseña MQTT
app.config['MQTT_REFRESH_TIME'] = 1.0  # Intervalo de actualización de mensajes MQTT



mqtt_client= Mqtt(app)
#socketio = SocketIO(app, logger=True,cors_allowed_origin='*')

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt_client.subscribe('temperatura_humedad')

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
     global temperatura, humedad , valor_updated, data_list, time_list,time_list2 , temp_list 
     
     payload = message.payload.decode() #payload tendra la temperatura y la humedad juntos y solo separado por una coma "temperatura,humedad"
     
     valor_updated = payload
     temperatura=payload[0:payload.index(',')]
     humedad=payload[payload.index(',')+1::]
     current_time = datetime.datetime.now().strftime('%H:%M:%S')
     hum= humedad
     temp= temperatura
     data_list.append(float(hum)) #cambiar por pulso cardiaco
     temp_list.append(float(temp)) # cambiar por Spo2
     time_list.append(current_time)
     time_list2.append(current_time)

     print(payload) 
     #socketio.emit('mqtt_message', data)
     #socketio.sleep(1)
    # Agregar esta línea para imprimir los valores recibidos


#----------------------------------------------#

#-------------Conectar con mysql---------------#
#conexion = MySQL(app) # se crea un vinculo entre mysql y mi aplicacion
#----------------------------------------------#
@app.route('/')
def index():
    #return("hola")
    
    data={
        'titulo': 'SpO2.IoT',
        
    }
    return render_template('index.html', data=data)

@app.route('/valores')
def mostrar_valores():
    return render_template('valores.html', temperatura=temperatura , humedad=humedad)

@app.get('/update')
def update():
    return valor_updated



def query_string():
    global id, last_name , first_name
    """"
    first_name = request.args['first_name']
    last_name = request.args['last_name']
    gender = request.args['gender']
    birth_date = request.args['birth_date']
    address = request.args['address']
    phone_number = request.args['phone_number']"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    gender = request.args.get('gender')
    birth_date = request.args.get('birth_date')
    address = request.args.get('address')
    phone_number = request.args.get('phone_number')
    pulse_data = data_list 
    spo2_data = temp_list
    fig1 = go.Figure(data=go.Scatter(y=pulse_data))
    fig2 = go.Figure(data=go.Scatter(y=spo2_data))
    
    # Configurar el diseño de la gráfica
    fig1.update_layout(title='Pulso en tiempo real', xaxis_title='Tiempo', yaxis_title='Pulso')
    fig2.update_layout(title='Oxigenacion de la sangre', xaxis_title='Tiempo', yaxis_title='Spo2')
    # Convertir la gráfica a formato JSON
    pulse_graph_json = fig1.to_json()
    spo2_graph_json = fig2.to_json()

    url = 'http://localhost:8080/fhir/Patient'
    json_data = {
        "resourceType": "Patient",
        "name": [
        {
            "use": "official",
            "given": [first_name],
            "family": last_name
        }
        ],
            "gender": gender,
            "birthDate": birth_date,
            "telecom": [
            {
                "value": str(phone_number),
                "use": "mobile",
                "system": "phone"
            },
            {
            "system": "email",
            "value": "jmapcl185@gmail.com"
            }
        ],
            "address": [
            {
            "line": [address],
            "city": "Lima",
            "postalCode": "2132"
              }
        ]
             }
            
        
    

    response = requests.post(url, json=json_data)

    print("First Name:", first_name)
    print("Last Name:", last_name)
    print("Gender:", gender)
    print("Birth Date:", birth_date)
    print("Address:", address)
    print("Phone Number:", phone_number) 

    if response.status_code == 201:
        print("Recurso creado exitosamente")
        patient_id = response.headers.get('Location')
        v1 = patient_id[35::].index("/")
        id = patient_id[35:35+v1]
        id = int(id)

        datos.append(last_name+" "+first_name)  

        with open("Pacientes.txt", "r") as archivo:
                contenido_existente = archivo.read()

        # Dividir el contenido en líneas
        lineas = contenido_existente.split("\n")

        # Verificar si cada valor ya está presente en el contenido
        valores_a_agregar = []
        for valor in datos:
            if valor not in lineas:
                valores_a_agregar.append(valor)

        # Agregar los valores que no estén presentes en el archivo al contenido
        nuevo_contenido = contenido_existente + "\n" + "\n".join(valores_a_agregar)

        # Escribir el nuevo contenido en el archivo
        with open("Pacientes.txt", "w") as archivo:
            archivo.write(nuevo_contenido)

        print("Valores agregados correctamente al archivo.")
        
        
        print(patient_id)
        print(id)

       
        

    else:
        print("Error al crear el recurso:", )
        #response.status_code
    return render_template('valores.html',pulse_graph=pulse_graph_json,spo2_graph=spo2_graph_json)

    

def  pagina_no_encontrada(error):
    return render_template('404.html'),404

#_------------------------------Codigo para hacer request al servidor FHIR--------------------------#
"""     requests.post(), requests.put() , requests.delete() , request.get() son los metodos de la libreria request 
        para poder crear , actualizar, eliminar y consultar los recursos en el servidor HAPI FHIR 
"""

#----------------------------------------------------------------------------------------------------#
@app.route('/Desarrollado')
def Desarrollado():
    return render_template("Desarrollado.html")

@app.route('/valores')
def valores():
    return render_template("valores.html")

@app.route('/contacto.html')
def contacto():
    return render_template("contacto.html")

#---------------------Configuracion web del Paciente----------------------------------------#
@app.route('/Paciente')
def Paciente():

    return render_template('Paciente.html')

@app.route('/Historial')
def Historial():
    return render_template('Historial.html')

@app.route('/Apuntes')
def Apuntes():
    return render_template('Apuntes.html')


#-------------------------------------------------------------------------------------------#

#-----------------POP UP------------------------------------------------------#
@app.route('/form', methods=['POST'])
def process_form():
    
    first_name = request.args['first_name']
    last_name = request.args['last_name']
    gender = request.args['gender']
    birth_date = request.args['birth_date']
    address = request.args['address']
    phone_number = request.args['phone_number']

    print("First Name:", first_name)
    print("Last Name:", last_name)
    print("Gender:", gender)
    print("Birth Date:", birth_date)
    print("Address:", address)
    print("Phone Number:", phone_number)
    
    
    return 'Formulario procesado exitosamente'
#--------------------------------------------------------------------------------------------#

#-----------------------------------------Dashboard-----------------------------------------------#
@app.get('/update_dash')
def update_dash():
    data_update_dash ={'pulse_data': data_list , 'time_data': time_list}
    data_update_dash_spo2 ={'spo2_data': temp_list , 'time_data2': time_list2}
    return data_update_dash,data_update_dash_spo2

@app.get('/update_dash_spo2')
def  update_dash_spo2():
    data_update_dash_spo2 ={'spo2_data': temp_list , 'time_data2': time_list2}
    return data_update_dash_spo2

#-------------------------------------------------------------------------------------------------#
#----------------------------Consulta de Informacion-POPUP-----------------------------------------#

#-------------------------------------------------------------------------------------------------#

@app.get('/Info')
def inf():
    I_D=id
    if I_D==None or I_D=="":
        return ""
    else:
        response = requests.get("http://localhost:8080/fhir/Patient/"+str(I_D))
        #formatted_json = json.dumps(response.json(), indent=4)
        r= json.loads(response.text)
        print(response.json())
        return  response.text
    
      

if __name__ == '__main__':
    
    app.add_url_rule('/query_string',view_func=query_string)
    app.register_error_handler(404,pagina_no_encontrada) 
    app.config.from_object(config['development'])
    #socketio.run(app, host='0.0.0.0', port=5000)
    app.run() 