from collections.abc import Mapping
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from experta import *
import json
from collections.abc import Mapping
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

with open('planes.json', 'r', encoding='utf-8') as f:
    planes = json.load(f)

## SISTEMA EXPERTO
    
class ICC(Fact):
    value = None

class Edad(Fact):
    value = None

class IMC(Fact):
    value = None

class Diabetes(Fact):
    value = None

class Hipertension(Fact):
    value = None

class EnfermedadCorazon(Fact):
    value = None

class ColesterolAlto(Fact):
    value = None

class TrigliceridosAlto(Fact):
    value = None

class NutritionPlan(KnowledgeEngine):

    @Rule(OR(IMC(value="Delgado"),
             Edad(value="Muy niño")), salience=10)
    def ruleDelgado(self):
        self.declare(Fact(plan="Regimen delgado"))

    @Rule(Hipertension(value='Si'),
          Diabetes(value='No'), salience=8)
    def ruleHipertension(self):
        self.declare(Fact(plan="Regimen hiposodico"))

    @Rule(Diabetes(value='Si'),
          Hipertension(value='No'), salience=8)
    def ruleDiabetes(self):
        self.declare(Fact(plan="Regimen hipoglucido"))

    @Rule(Diabetes(value='Si'),
          Hipertension(value='Si'), salience=9)
    def ruleDiabetesHipertension(self):
        self.declare(Fact(plan="Regimen hipoglucido-hiposodico"))

    @Rule(IMC(value='Normal'),
          Diabetes(value='No'),
          Hipertension(value='No'),
          OR(
            OR(ICC(value='Grave'),
                ICC(value='Preocupante')),
            EnfermedadCorazon(value='Si'),
            TrigliceridosAlto(value='Si'),
            ColesterolAlto(value='Si')
          ),
          salience=7)
    def ruleHipograso(self):
        self.declare(Fact(plan="Regimen hipograso"))

    @Rule(OR(IMC(value='Sobrepeso'),
             IMC(value='Obeso')), 
        Edad(value="Niño"), salience=7)
    def ruleSobrepesoNiño(self):
        self.declare(Fact(plan="Regimen sobrepeso-obesidad niño"))

    @Rule(OR(IMC(value='Sobrepeso'),
             IMC(value='Obeso')),
            Edad(value='Adulto'),
            salience=7)
    def ruleSobrepeso(self):
        self.declare(Fact(plan="Regimen sobrepeso-obesidad"))

## API

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
jwt = JWTManager(app)
CORS(app)
expires = timedelta(days=36500)

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    usuario = db.Column(db.String(255), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False, )

class NutritionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    request_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, request_data):
        self.user_id = user_id
        self.request_data = request_data

@app.route('/registro', methods=['POST'])
def registro():
    data = request.json
    if not all(field in data for field in ['nombre', 'usuario', 'password']):
        return jsonify({'error': 'Falta nombre, usuario o contraseña'}), 400

    hashed_password = generate_password_hash(data['password'])
    nuevo_usuario = Usuario(nombre=data['nombre'], usuario=data['usuario'], contraseña=hashed_password)
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        access_token = create_access_token(identity=nuevo_usuario.id, expires_delta=expires)
        return jsonify({'mensaje': 'Usuario registrado exitosamente', 'access_token': access_token}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'El nombre de usuario ya existe'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not all(field in data for field in ['usuario', 'password']):
        return jsonify({'error': 'Falta usuario o contraseña'}), 400

    usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
    if usuario and check_password_hash(usuario.contraseña, data['password']):
        access_token = create_access_token(identity=usuario.id, expires_delta=expires)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'mensaje': 'Usuario o contraseña incorrectos'}), 401

@app.route('/prueba', methods=['GET'])
@jwt_required(optional=True)
def prueba_endpoint():
    current_user_id = get_jwt_identity()
    if current_user_id:
        return jsonify({'id del usuario': current_user_id}), 200
    else:
        return jsonify({'mensaje': 'No está logeado'}), 200

@app.route('/mis_datos', methods=['GET'])
@jwt_required()
def obtener_mis_datos():
    user_id = get_jwt_identity()
    try:
        usuario = Usuario.query.filter_by(id=user_id).first()
        if usuario:
            datos_usuario = {
                'nombre': usuario.nombre,
                'usuario': usuario.usuario,
            }
            return jsonify(datos_usuario), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': 'No se pudieron obtener los datos del usuario'}), 500

@app.route('/mis_planes', methods=['GET'])
@jwt_required()
def obtener_mis_planes():
    user_id = get_jwt_identity()
    try:
        planes = NutritionRequest.query.filter_by(user_id=user_id).order_by(NutritionRequest.created_at.desc()).all()
        lista_planes = [{'id': plan.id, 'datos': plan.request_data, 'creado_en': plan.created_at} for plan in planes]
        return jsonify(lista_planes), 200
    except Exception as e:
        return jsonify({'error': 'No se pudieron obtener los planes'}), 500

@app.route('/get_plan', methods=['POST'])
@jwt_required(optional=True)
def get_nutrition_plan():
    user_id = get_jwt_identity()
    data = request.get_json()

    campos_requeridos = ['genero', 'edad', 'peso', 'talla', 'diabetes', 'hipertension',
                         'circunferencia_cintura', 'circunferencia_cadera',
                         'enfermedad_corazon', 'colesterol_alto', 'trigliceridos_alto']

    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"error": "Faltan datos requeridos"}), 400
    for campo in campos_requeridos:
        if data.get(campo) is None:
            return jsonify({"error": f"Campo {campo} no puede ser nulo"}), 400

    try:
        edad = int(data.get('edad'))
        peso = float(data.get('peso'))
        talla = float(data.get('talla'))
        circunferencia_cintura = float(data.get('circunferencia_cintura'))
        circunferencia_cadera = float(data.get('circunferencia_cadera'))
        if edad < 0 or peso <= 0 or talla <= 0 or circunferencia_cintura <= 0 or circunferencia_cadera <= 0:
            return jsonify({"error": "Los valores numéricos deben ser positivos"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Datos numéricos inválidos"}), 400

    campos_texto = ['diabetes', 'hipertension', 'enfermedad_corazon', 'colesterol_alto', 'trigliceridos_alto']
    for campo in campos_texto:
        valor = data.get(campo)
        if not isinstance(valor, str) or valor.capitalize() not in ["Si", "No"]:
            return jsonify({"error": "Datos inválidos en el campo " + campo}), 400

    genero = data.get('genero')
    if not isinstance(genero, str) or genero not in ["m", "f"]:
        return jsonify({"error": "Datos inválidos en el campo genero"}), 400

    edad_num = data.get('edad')
    if edad_num <= 5:
        edad = "Muy niño"
    elif edad_num <= 11:
        edad = "Niño"
    else:
        edad = "Adulto"

    peso = data.get('peso', 0)
    talla = data.get('talla', 0)
    valor_imc = peso / (talla / 100) ** 2 if talla > 0 else 0
    if valor_imc < 18.5:
        imc = "Delgado"
    elif 18.5 <= valor_imc < 25:
        imc = "Normal"
    elif 25 <= valor_imc < 30:
        imc = "Sobrepeso"
    else:
        imc = "Obeso"

    if genero == 'm':
        if circunferencia_cintura < 94:
            icc = "Normal"
        elif circunferencia_cintura <= 102:
            icc = "Preocupante"
        else:
            icc = "Grave"
    elif genero == 'f':
        if circunferencia_cintura < 80:
            icc = "Normal"
        elif circunferencia_cintura <= 88:
            icc = "Preocupante"
        else:
            icc = "Grave"

    engine = NutritionPlan()
    engine.reset()
    engine.declare(Edad(value=edad),
                   IMC(value=imc),
                   ICC(value=icc),
                   Diabetes(value=data.get('diabetes').capitalize()),
                   Hipertension(value=data.get('hipertension').capitalize()),
                   EnfermedadCorazon(value=data.get('enfermedad_corazon').capitalize()),
                   ColesterolAlto(value=data.get('colesterol_alto').capitalize()),
                   TrigliceridosAlto(value=data.get('trigliceridos_alto').capitalize()))

    engine.run()
    print(engine.facts.values())
    plan = next((fact['plan'] for fact in engine.facts.values() if 'plan' in fact),
                "Regimen hipograso")
    facts = {
        "edad_val": edad,
        "imc": imc,
        "icc": icc,
        "valor_imc": valor_imc
    }
    if user_id:
        new_request = NutritionRequest(user_id=user_id, request_data={**facts, **data})
        db.session.add(new_request)
        db.session.commit()
    return jsonify({"plan": planes[plan], "Nombre regimen": plan, "facts": facts})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG_MODE')
    app.run(host= '0.0.0.0', port = port, debug=bool(debug))
