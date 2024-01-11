from collections.abc import Mapping
from flask import Flask, request, jsonify
from flask_cors import CORS
from experta import KnowledgeEngine, Rule, Fact, DefFacts, AS, P
import json
from collections.abc import Mapping
from flask_cors import CORS

with open('planes.json', 'r', encoding='utf-8') as f:
    planes = json.load(f)

app = Flask(__name__)
CORS(app)

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

    @Rule(IMC(value="Delgado"))
    def ruleDelgado(self):
        self.declare(Fact(plan="Regimen delgado"))

    @Rule(Hipertension(value='Si'))
    def ruleHipertension(self):
        self.declare(Fact(plan="Regimen hiposodico"))

    @Rule(Diabetes(value='Si'))
    def ruleDiabetes(self):
        self.declare(Fact(plan="Regimen hipoglucida"))

    @Rule(EnfermedadCorazon(value='Si'))
    def ruleCorazon(self):
        self.declare(Fact(plan="Regimen hipograso"))

    @Rule(ColesterolAlto(value='Si'))
    def ruleColesterol(self):
        self.declare(Fact(plan="Regimen hipograso"))

    @Rule(TrigliceridosAlto(value='Si'))
    def ruleTrigliceridos(self):
        self.declare(Fact(plan="Regimen hipograso"))

    @Rule(IMC(value='Sobrepeso'), Edad(value="Niño"))
    def ruleSobrepesoNiño(self):
        self.declare(Fact(plan="Regimen sobrepeso-obesidad niño"))

    @Rule(IMC(value='Obeso'), Edad(value="Niño"))
    def ruleObesoNiño(self):
        self.declare(Fact(plan="Regimen sobrepeso-obesidad niño"))

    @Rule(IMC(value='Sobrepeso'))
    def ruleSobrepeso(self):
        self.declare(Fact(plan="Regimen sobrepeso-obesidad"))

    @Rule(IMC(value='Obeso'))
    def ruleObeso(self):
        self.declare(Fact(plan="Regimen sobrepeso-obesidad"))

    @Rule(ICC(value='Grave'))
    def ruleIccGrave(self):
        self.declare(Fact(plan="Regimen hipograso"))

    @Rule(ICC(value='Preocupante'))
    def ruleIccPreocupante(self):
        self.declare(Fact(plan="Regimen hipograso"))

    @Rule(IMC(value='Normal'))
    def ruleNormal(self):
        self.declare(Fact(plan="Regimen hipograso"))

@app.route('/get_plan', methods=['POST'])
def get_nutrition_plan():
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

    edad = "Niño" if data.get('edad', 0) < 15 else "Adulto"
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

    plan = next((fact['plan'] for fact in engine.facts.values() if 'plan' in fact),
                "Regimen hipograso")
    facts = {
        "edad": edad,
        "imc": imc,
        "icc": icc
    }
    return jsonify({"plan": planes[plan], "Nombre regimen": plan, "facts": facts})

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port = 5000, debug=True)
