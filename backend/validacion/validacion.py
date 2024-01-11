import requests
import json
import pandas as pd

ruta_archivo_json = 'entradas.json'

# Leer el archivo JSON con los escenarios de prueba
with open(ruta_archivo_json, 'r') as file:
    pacientes = json.load(file)

url = 'http://localhost:5000/get_plan'

resultados = []

for paciente in pacientes:
    try:
        response = requests.post(url, json=paciente)

        if response.status_code == 200:
            data = response.json()
            nombre_regimen = data.get('Nombre regimen', 'No disponible')
            facts = data.get('facts', 'No disponible')
            resultados.append({'Nombre regimen': nombre_regimen,  'facts': json.dumps(facts), 'JSON Enviado': json.dumps(paciente)})
        elif response.status_code == 400:
            error_message = response.json().get('error', 'Error desconocido')
            resultados.append({'Error': error_message, 'JSON Enviado': json.dumps(paciente)})
        else:
            resultados.append({'Error': f'Error inesperado: {response.status_code}', 'JSON Enviado': json.dumps(paciente)})
    
    except Exception as e:
        resultados.append({'Error': f'Excepción durante la solicitud: {str(e)}', 'JSON Enviado': json.dumps(paciente)})

df = pd.DataFrame(resultados)
nombre_archivo_salida = 'resultados_sistema_experto.csv'
df.to_csv(nombre_archivo_salida, index=False)
print(f'Resultados guardados en {nombre_archivo_salida}')