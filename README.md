# SE-Nutrición Backend

Este repositorio contiene el backend para el sistema SE-Nutrición, una aplicación destinada a proporcionar planes de nutrición personalizados.

## Iniciar y Detener el Backend

Para iniciar o detener el backend, se utiliza el workflow de GitHub Actions:

- **Iniciar**: Para iniciar el backend `start`.
- **Detener**: Para detener el backend después de probaro `stop`.

El workflow se encuentra en `start_stop_api.yaml` y puede ser activado desde la sección de Actions de GitHub.
https://github.com/ImagineBrkr/se-nutricion-backend/actions/workflows/start_stop_api.yaml

## Estructura de la Petición (Request)

Para realizar una petición al backend, debes enviar un JSON con la siguiente estructura:

```json
{
    "genero": "m",
    "edad": 25,
    "peso": 40.0,
    "talla": 120.0,
    "circunferencia_cintura": 80.0,
    "circunferencia_cadera": 95.0,
    "diabetes": "no",
    "hipertension": "si",
    "enfermedad_corazon": "si",
    "colesterol_alto": "no",
    "trigliceridos_alto": "si"
}
```

### Campos del Request

- `genero`: String  (`m` o `f`).
- `edad`: Entero.
- `peso`: Float.
- `talla`: Float.
- `circunferencia_cintura`: Float.
- `circunferencia_cadera`: Float.
- `diabetes`: String (`si` o `no`).
- `hipertension`: String (`si` o `no`).
- `enfermedad_corazon`: String (`si` o `no`).
- `colesterol_alto`: String (`si` o `no`).
- `trigliceridos_alto`: String (`si` o `no`).


## Estructura de la Respuesta (Response)

### Código 200

Si la petición es exitosa, el response tendrá el siguiente formato:

```json
{
    "plan": {
        "Nro_comidas": "int (número de comidas por día)",
        "Recomendaciones": [
            "string (lista de recomendaciones generales)"
        ],
        "Alimentos": [
            {
                "Tipo": "string (tipo de alimento)",
                "Raciones": "int (cantidad recomendada) (OPCIONAL)",
                "Frecuencia": "string (frecuencia de consumo)",
                "Cantidad": "string (medida de la porción) (OPCIONAL)",
                "Opciones": [
                    "string (opciones disponibles del alimento)"
                ],
                "Preparacion": "string (método de preparación sugerido) (OPCIONAL)"
            }
        ]
    },
    "facts": {
        "edad": "string (niño, adulto)",
        "imc": "string (delgado, normal, sobrepeso, obeso)"
    }
}
```

### Código 400
```json
{
    "error": "string con el error"
}
```