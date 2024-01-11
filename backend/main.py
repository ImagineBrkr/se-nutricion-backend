from collections.abc import Mapping
from flask import Flask, request, jsonify
from experta import KnowledgeEngine, Rule, Fact, DefFacts, AS, P
import json
from collections.abc import Mapping

with open('planes.json', 'r', encoding='utf-8') as f:
    planes = json.load(f)

app = Flask(__name__)

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

class NivelColesterol(Fact):
    value = None

class NivelTrigliceridos(Fact):
    value = None

class NutritionPlan(KnowledgeEngine):

    @Rule(IMC(value="Delgado"))
    def rule1(self):
        self.declare(Fact(plan=planes["Regimen delgado"]))

    @Rule(IMC(value='Sobrepeso'))
    def rule2(self):
        self.declare(Fact(plan=planes["Regimen sobrepeso-obesidad"]))

    @Rule(IMC(value='Obeso'))
    def rule3(self):
        self.declare(Fact(plan=planes["Regimen sobrepeso-obesidad"]))

    @Rule(Hipertension(value='SI'))
    def rule4(self):
        self.declare(Fact(plan=planes["plan 1"]))

@app.route('/get_plan', methods=['POST'])
def get_nutrition_plan():
    data = request.get_json()

    campos_requeridos = ['genero', 'edad', 'peso', 'talla', 'diabetes', 'hipertension',
                         'circunferencia_cintura', 'circunferencia_cadera',
                         'enfermedad_corazon', 'colesterol_alto', 'trigliceridos_alto']

    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    try:
        edad = int(data.get('edad'))
        peso = float(data.get('peso'))
        talla = float(data.get('talla'))
        circunferencia_cintura = float(data.get('circunferencia_cintura'))
        circunferencia_cadera = float(data.get('circunferencia_cadera'))
    except ValueError:
        return jsonify({"error": "Datos numéricos inválidos"}), 400
    
    campos_texto = ['diabetes', 'hipertension', 'enfermedad_corazon', 'colesterol_alto', 'trigliceridos_alto']
    for campo in campos_texto:
        valor = data.get(campo)
        if not isinstance(valor, str) or valor.capitalize() not in ["Si", "No"]:
            return jsonify({"error": "Datos inválidos en el campo " + campo}), 400
    
    genero = data.get('genero')
    if not isinstance(genero, str) or genero not in ["m", "f"]:
        return jsonify({"error": "Datos inválidos en el campo genero"}), 400

    edad = "Niño" if data.get('edad', 0) < 18 else "Adulto"
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
                   NivelColesterol(value=data.get('colesterol_alto').capitalize()),
                   NivelTrigliceridos(value=data.get('trigliceridos_alto').capitalize()))

    engine.run()

    plan = next((fact['plan'] for fact in engine.facts.values() if 'plan' in fact),
                {"Resultado": 'Plan no encontrado'})
    facts = {
        "edad": edad,
        "imc": imc

    }
    return jsonify({"plan": dict(plan), "facts": facts})

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port = 5000, debug=True)
