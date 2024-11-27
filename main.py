from datetime import datetime, timezone
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import paho.mqtt.client as mqtt

from gemini import gera_prompt
from gmail import enviar_email

#Conexão com banco de dados

#nome da aplicação
app = Flask('registro')

#configura o SQLALchemy para rastrear modificações
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:senai%40134@127.0.0.1/bd_medidor'

mybd = SQLAlchemy(app)

#Conexão com sensores
mqtt_dados = {}

def conexao_sensor(cliente, userdata, flags, rc):
    cliente.subscribe("projeto_integrado/SENAI134/Cienciadedados/Grupo1")

def msg_sensor(client, userdata, msg):
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
            co2 = mqtt_dados.get('CO2')
            poeira = 0
            tempo_registro = mqtt_dados.get('timestamp')

            if tempo_registro is None:
                print("Timestamp não encontrado")
            
            try:
                tempo_oficial = datetime.fromtimestamp(int(tempo_registro), tz=timezone.utc)
            except(ValueError, TypeError) as e:
                print(f"Erro ao converter timestamp: {str(e)}")
                return
            
            #criar o objeto que vai simular a tabela do banco
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
            
            if (umidade < 45 or temperatura > 40 or temperatura < 15):
                esqueleto = """<!DOCTYPE html>
                                <html>
                                <head>
                                <style>
                                body {
                                background-color: #f2f2f2;
                                font-family: Arial, sans-serif;
                                }

                                .container {
                                background-color: #fff;
                                border-radius: 10px;
                                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                padding: 20px;
                                margin: 20px auto;
                                max-width: 600px;
                                }

                                .header {
                                background-color: #ff7f50; /* Laranja vibrante */
                                color: #fff;
                                padding: 10px;
                                border-radius: 5px 5px 0 0;
                                }

                                .content {
                                padding: 20px;
                                }

                                .data {
                                font-size: 18px;
                                font-weight: bold;
                                margin-bottom: 10px;
                                }

                                .data span {
                                color: #ff8c00; /* Laranja mais escuro */
                                }

                                .warning {
                                background-color: #ffcccb; /* Rosa claro */
                                border: 1px solid #ff7f50; /* Borda laranja */
                                padding: 10px;
                                margin: 20px 0;
                                border-radius: 5px;
                                }
                                </style>
                                </head>
                                <body>
                                <div class="container">
                                <div class="header">
                                    <h2>Alerta de Danos à Plantação</h2>
                                </div>
                                <div class="content">
                                    <p>
                                    Esta é uma mensagem de alerta sobre possíveis danos à sua plantação!
                                    </p>
                                    <div class="data">
                                    <span>Umidade:</span> 79%
                                    </div>
                                    <div class="data">
                                    <span>Temperatura:</span> 24.48°C
                                    </div>
                                    <div class="warning">
                                    As condições atuais podem causar danos à sua plantação! Monitoramento constante é necessário.
                                    </div>
                                </div>
                                </div>
                                </body>
                                </html>"""
                body = gera_prompt(esqueleto, temperatura, umidade, co2)
                enviar_email("Alerta de agora", "mvinicius.oliveira04@gmail.com", body)
                print("Email enviado!")

            print("Dados foram inseridos com sucesso no banco!")

        except Exception as e:
            print(f"Erro ao processar os dados do MQTT: {str(e)}")
            mybd.session.rollback()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = conexao_sensor
mqtt_client.on_message = msg_sensor
mqtt_client.connect("test.mosquitto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()

class Registro(mybd.Model):
    __tablename__ = 'tb_registro'
    id = mybd.Column(mybd.Integer, primary_key=True, autoincrement=True)
    temperatura = mybd.Column(mybd.NUMERIC(10,2))
    pressao = mybd.Column(mybd.NUMERIC(10,2))
    altitude = mybd.Column(mybd.NUMERIC(10,2))
    umidade = mybd.Column(mybd.NUMERIC(10,2))
    co2 = mybd.Column(mybd.NUMERIC(10,2))
    poeira = mybd.Column(mybd.NUMERIC(10,2))
    tempo_registro = mybd.Column(mybd.DateTime)

# -------------------------------------------------

# ------------------- GET(ID) ---------------------
@app.route("/registros/<id>", methods=["GET"])
def seleciona_registro_id(id):
    registro_objetos = Registro.query.filter_by(id=id).first()

    if(registro_objetos == None):
        return gera_response(404, "registro", {}, "Registro não encontrado!")

    registro_json = registro_objetos.to_json()

    return gera_response(200, "registro", registro_json)

# --------------------- GET -----------------------
@app.route("/registros", methods=["GET"])
def selecionar_registros():
    registro_objetos = Registro.query.all()

    registro_json = [registro.to_json() for registro in registro_objetos]

    return gera_response(200, "registro", registro_json)

# --------------------- POST ----------------------
@app.route("/registros", methods=["POST"])
def criar_registro():
    body = request.get_json()
    try:
        registro = Registro(
            temperatura = body["temperatura"],
            pressao = body["pressao"],
            altitude = body["altitude"],
            umidade = body["umidade"],
            co2 = body["CO2"],
            #poeira = body["poeira"],
            tempo_registro = body["tempo_registro"]
        )

        mybd.session.add(registro)
        mybd.session.commit()

        return gera_response(201, "registro", registro.to_json(), "Criado com Sucesso!!!")
    
    except Exception as e:
        print('Erro', e)

        return gera_response(400, "registro", {}, "Erro ao cadastrar!!!")

# ------------------ DELETE ---------------------
@app.route("/registros/<id>", methods=["DELETE"])
def deletar_registro(id):
    registro_objeto = Registro.query.filter_by(id=id).first()

    if(registro_objeto == None):
        return gera_response(404, "registro", {}, "Registro não encontrado!")
    try:
        mybd.session.delete(registro_objeto)
        mybd.session.commit()

        return gera_response(200, "registro", {}, "Deletado com sucesso!")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "registro", {}, "Erro ao deletar")

# ------------- GET - Sensores -------------------
@app.route("/dados", methods=["GET"])
def busca_dados():
    return jsonify(mqtt_dados)

def to_json(self):
        return {
            "id": self.id,
            "temperatura": float(self.temperatura),
            "pressao": float(self.pressao),
            "altitude": float(self.altitude),
            "umidade": float(self.umidade),
            "co2": float(self.co2),
            #"poeira": float(self.poeira),
            "tempo_registro": self.tempo_registro.strftime('%Y-%m-%d %H:%M:%S')
            if self.tempo_registro else None
        }

# ------------- POST - Sensores ------------------
@app.route("/dados", methods=['POST'])
def criar_dados():
    try:
        dados = request.get_json()

        if not dados:
            return jsonify({"error": "Nenhum dado fornecido"}), 400
        
        print(f"Dados Recebidos{dados}")
        temperatura = dados.get('temperatura')
        pressao = dados.get('pressao')
        altitude = dados.get('altitude')
        umidade = dados.get('umidade')
        co2 = dados.get('CO2')
        timestamp_unix = dados.get('tempo_registro')

        try:
            tempo_oficial = datetime.fromtimestamp(int(timestamp_unix), tz=timezone.utc)
        except Exception as e:
            print("Erro", e)
            return gera_response(400, "Timestamp Inválido")
        
        # Cria o objeto de Registro
        novo_registro = Registro(
            temperatura = temperatura,
            pressao = pressao,
            altitude = altitude,
            umidade = umidade,
            co2 = co2,
            tempo_registro = tempo_oficial,
        )

        mybd.session.add(novo_registro)
        print("Adicionando o novo registro")

        mybd.session.commit()
        print("Dados inseridos no banco de dados com sucesso!")
    except Exception as e:
        print(f"Erro ao processar a solicitação")
        mybd.session.rollback()
        return gera_response(500, "Falha ao processar dados")

# --------------------- Retorno -----------------------
def gera_response(status, nome_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")

if __name__ == '__main__':
    with app.app_context():
        mybd.create_all()

        start_mqtt()
        app.run(port=5000, host="localhost", debug=True)