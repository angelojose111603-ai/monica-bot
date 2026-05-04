const { Groq } = require("groq-sdk");

const MONICA_SYSTEM_PROMPT = `
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
`;

exports.handler = async (event, context) => {
  // Solo permitir POST
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    const { message, history } = JSON.parse(event.body);
    const apiKey = process.env.GROQ_API_KEY;

    if (!apiKey) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: "GROQ_API_KEY no configurada en Netlify" }),
      };
    }

    const groq = new Groq({ apiKey });

    const messages = [
      { role: "system", content: MONICA_SYSTEM_PROMPT },
      ...history,
      { role: "user", content: message }
    ];

    const completion = await groq.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      messages,
      temperature: 0.7,
      max_tokens: 150,
    });

    const responseText = completion.choices[0].message.content;

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
      body: JSON.stringify({ response: responseText }),
    };
  } catch (error) {
    console.error("Error Groq:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
