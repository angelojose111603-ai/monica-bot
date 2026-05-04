import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    api_key = api_key.strip()
    print(f"CARGANDO GROQ CON LLAVE: {api_key[:10]}...{api_key[-5:]}")
else:
    print("ALERTA: No se encontró GROQ_API_KEY en el .env")

client = Groq(api_key=api_key)

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

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": "system", "content": MONICA_SYSTEM_PROMPT}]
        messages.extend(request.history)
        messages.append({"role": "user", "content": request.message})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=150,
        )

        response_text = completion.choices[0].message.content
        return {"response": response_text}
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR GROQ: {error_msg}")
        # Intentar extraer el mensaje de error de Groq si es un JSON
        try:
            if hasattr(e, 'response'):
                error_detail = e.response.json()
                error_msg = error_detail.get('error', {}).get('message', error_msg)
        except:
            pass
        raise HTTPException(status_code=500, detail=error_msg)

from fastapi.responses import HTMLResponse, FileResponse

@app.get("/{filename}.png")
async def get_image(filename: str):
    # Intentar buscar el archivo en el directorio actual
    possible_files = [f"{filename}.png", "logo.png", "avatar.png"]
    for f in possible_files:
        if os.path.exists(f):
            if filename in f or f == f"{filename}.png":
                return FileResponse(f)
    
    # Fallback si el nombre exacto no coincide pero es uno de los conocidos
    if "logo" in filename.lower() and os.path.exists("logo.png"):
        return FileResponse("logo.png")
    if "avatar" in filename.lower() and os.path.exists("avatar.png"):
        return FileResponse("avatar.png")
        
    return {"error": "Image not found", "tried": filename}

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
