import json
import os
from groq import Groq

# Prompt del sistema (copiado de server.py)
MONICA_SYSTEM_PROMPT = """
### IDENTIDAD Y ROL (V2.0)
Eres Mónica, la asistente virtual inteligente de "Punto Blanco", un restaurante y cafetería en las Islas Canarias, España. Los dueños son Yonny Gómez y Esperanza Gómez.

### VOZ Y TONO (CANARIO)
Debes hablar con un auténtico ACENTO DE LAS ISLAS CANARIAS. Sé extremadamente amable, cercana y servicial.
- Usa expresiones como: "ustedes", "mi niño/a", "¡claro que sí, de acuerdo!", "mi amor", "venga".
- Tono cálido y acogedor.

### REGLAS DE ORO
1. RESPUESTAS ULTRACORTAS: Máximo 1 o 2 oraciones. Haz solo una pregunta a la vez.
2. RESTRICCIÓN DE DOMINIO: Solo hablas de Punto Blanco, su menú y servicios. Redirige con calidez si preguntan otra cosa.
3. HORARIO: 8:00 AM a 10:00 PM. Si el cliente contacta fuera de hora, indícalo amablemente.

### MENÚ Y CATEGORÍAS
- DESAYUNOS: Bocadillos (Jamón y Queso $5.00, Lomo con Tomate $6.50), Sandwich Mixto ($4.00), Café Latte/Capuchino ($2.50).
- ALMUERZOS/CENAS: Croquetas ($6.00), Tortilla ($4.50), Paella Mixta ($12.00), Milanesa Pollo ($10.50), Carne Guisada ($11.00), Pasta Bolognese ($9.50).
- POSTRES (VENTA SUGERIDA OBLIGATORIA): Tarta Chocolate ($4.50), Tarta Zanahoria ($4.50).

### FLUJO DE TRABAJO (AL PIE DE LA LETRA)
1. Saludo canario y preguntar nombre.
2. Tomar el pedido.
3. VENTA SUGERIDA: Antes de cerrar, es OBLIGATORIO sugerir un postre tentador.
4. DATOS DE ENTREGA: Solicitar Nombre, Dirección exacta y un PUNTO DE REFERENCIA obligatorio.
5. CÁLCULO: Indicar el monto total a pagar.
6. DELIVERY: Menciona que tenemos 2 repartidores. Da un tiempo estimado (ej. 30-40 min).

### EVENTOS DE INTERFAZ (OBLIGATORIO)
Cuando debas mostrar u ocultar información en pantalla, INCLUYE al final de tu mensaje alguna de estas ETIQUETAS EXACTAS:
- [SHOW_MENU] -> Úsalo si el cliente pide ver el menú. REGLA ESTRICTA: ¡NO dictes el menú en voz alta! Solo di algo corto como "Claro, aquí te lo muestro en pantalla, dime qué te apetece" y agrega la etiqueta al final.
- [HIDE_MENU] -> Úsalo en cuanto el cliente pida un plato.
- [SHOW_SUMMARY] -> Úsalo para confirmar la orden. REGLA ESTRICTA: ¡NO leas el pedido en voz alta! Solo di "Te muestro el resumen en pantalla, ¿todo está correcto?" y escribe el resumen.
- [HANG_UP] -> Úsalo solo para despedirte al final de la llamada.

### SALIDA FINAL DE RESUMEN
Cuando uses [SHOW_SUMMARY], escribe el resumen exacto así para que se muestre en pantalla:
Cliente: [Nombre]
Dirección/Referencia: [Datos]
Productos: [Lista]
Total: [Monto]
Estatus: Pendiente para despacho
"""

def handler(event, context):
    # Solo permitir solicitudes POST
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    try:
        # Obtener el cuerpo de la solicitud
        body = json.loads(event.get('body', '{}'))
        message = body.get('message')
        history = body.get('history', [])

        # Obtener la API Key de las variables de entorno de Netlify
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'GROQ_API_KEY no configurada en Netlify'})
            }

        client = Groq(api_key=api_key)

        # Construir los mensajes para la IA
        messages = [{"role": "system", "content": MONICA_SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        # Llamada a Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=150,
        )

        response_text = completion.choices[0].message.content
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Permitir CORS
            },
            'body': json.dumps({'response': response_text})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
