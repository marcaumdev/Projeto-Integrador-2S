from datetime import datetime, timezone
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import paho.mqtt.client as mqtt

#Conexão com banco de dados

#nome da aplicação
app = Flask('registro')

#configura o SQLALchemy para rastrear modificações
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root://root:senai%40134@127.0.0.1/bd_medidor'

mybd = SQLAlchemy(app)

#Conexão com sensores
mqtt_dados = {}

def conexao_sensor(cliente, rc):
    cliente.subcribe("projeto_integrado/SENAI134/Cienciadedados/GrupoX")

def msg_sensor(msg):
    global mqtt_dados
    #decofificar a mensagem recebida de bytes para string
    valor = msg.payload.decode('utf-8')
    #decodificar de string para json
    mqtt_dados = json.loads(valor)

    print(f"Mensagem Recebida: {mqtt_dados}")

    with app.app_context():
        try:
            temperatura = mqtt_dados.get('temperature')
            pressao = mqtt_dados.get('pressure')
            altitude = mqtt_dados.get('altitude')
            umidade = mqtt_dados.get('humidity')
            co2 = mqtt_dados.get('co2')
            poeira = 0
            tempo_registro = mqtt_dados.get('timestamps')

            if tempo_registro is None:
                print("Timestamp não encontrado")
            
            try:
                tempo_oficial = datetime.fromtimestamp(int(tempo_registro), tz=timezone.utc)
            except(ValueError, TypeError) as e:
                print(f"Erro ao converter timestamp: {str(e)}")
                return
            
            #criar p objetivo que vai simular a tabela do banco
            novos_dados = Registro(
	            temperatura = temperatura,
                pressao = pressao,
                altitude = altitude,
                umidade = umidade,
                co2 = co2,
                poeira = poeira,
                tempo_registro = tempo_oficial
            )

            #adicionar novo registro ao banco

            mybd.session.add(novos_dados)
            mybd.session.commit()

        except Exception as e:
            print(f"Erro ao processar os dados do MQTT: {str(e)}")
            mybd.session.rollback()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = conexao_sensor
mqtt_client.on_message = msg_sensor
mqtt_client.connect("test.mosqutto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()