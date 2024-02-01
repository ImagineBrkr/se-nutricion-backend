import requests
import random
import json
import pandas as pd

ruta_archivo_json = 'entradas.json'

# Leer el archivo JSON con los escenarios de prueba
with open(ruta_archivo_json, 'r') as file:
    pacientes = json.load(file)

url = 'http://localhost:5000/get_plan'

def generar_json_prueba(num_pruebas: int):
    generos = ["m", "f"]
    respuestas_binarias = ["si", "no"]

    pruebas = []
    for _ in range(num_pruebas):
        json_prueba = {
            "genero": random.choice(generos),
            "edad": random.randint(18, 100),
            "peso": round(random.uniform(40.0, 120.0), 1),
            "talla": round(random.uniform(1.5, 2.0), 2),
            "circunferencia_cintura": round(random.uniform(60.0, 120.0), 1),
            "circunferencia_cadera": round(random.uniform(70.0, 150.0), 1),
            "diabetes": random.choice(respuestas_binarias),
            "hipertension": random.choice(respuestas_binarias),
            "enfermedad_corazon": random.choice(respuestas_binarias),
            "colesterol_alto": random.choice(respuestas_binarias),
            "trigliceridos_alto": random.choice(respuestas_binarias)
        }
        pruebas.append(json_prueba)

    return pruebas

def guardar_json_prueba():
    try:
        with open(ruta_archivo_json, 'r') as file:
            datos_existentes = json.load(file)
    except FileNotFoundError:
        datos_existentes = []
    nuevos_jsons = generar_json_prueba(100)
    datos_actualizados = datos_existentes + nuevos_jsons
    with open(ruta_archivo_json, 'w') as file:
        json.dump(datos_actualizados, file, indent=2)

    print(f"JSONs agregados al archivo {ruta_archivo_json}")

resultados = []

for paciente in pacientes:
    try:
        response = requests.post(url, json=paciente)

        if response.status_code == 200:
            data = response.json()
            nombre_regimen = data.get('Nombre regimen', 'No disponible')
            facts = data.get('facts', 'No disponible')
            resultados_paciente = paciente.copy()
            resultados_paciente.update({
                "plan": nombre_regimen
            })
            resultados.append(resultados_paciente)
        elif response.status_code == 400:
            error_message = response.json().get('error', 'Error desconocido')
            # resultados.append({'Nombre regimen': 'No regimen', 'facts': 'Error', 'Error': error_message, 'JSON Enviado': json.dumps(paciente)})
        else:
            pass
            # resultados.append({'Nombre regimen': 'No regimen', 'facts': 'Error', 'Error': f'Error inesperado: {response.status_code}', 'JSON Enviado': json.dumps(paciente)})
    
    except Exception as e:
        pass
        # resultados.append({'Error': f'Excepción durante la solicitud: {str(e)}', 'JSON Enviado': json.dumps(paciente)})
    print(resultados[-1])


df = pd.DataFrame(resultados)
nombre_archivo_salida = 'resultados_sistema_experto.csv'
df.to_csv(nombre_archivo_salida, index=False)
print(f'Resultados guardados en {nombre_archivo_salida}')