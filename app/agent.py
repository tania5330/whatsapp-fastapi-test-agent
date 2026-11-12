def build_reply(message_text: str) -> str:
    """Simple rule-based demo agent. Replace this function with an LLM later."""
    text = (message_text or "").strip().lower()

    if not text:
        return "¡Hola! Soy tu agente virtual de prueba. ¿En qué puedo ayudarte?"
    if any(word in text for word in ("hola", "buenas", "hello", "hi")):
        return (
            "¡Hola! 👋 Soy tu agente virtual de prueba. "
            "Ya estoy conectado a WhatsApp. Puedes escribirme: ayuda, horario o precio."
        )
    if "ayuda" in text or "opciones" in text:
        return "Puedo responder consultas de prueba. Escribe *horario*, *precio* o *contacto*."
    if "horario" in text:
        return "Nuestro horario de atención de prueba es de lunes a viernes, de 9:00 a 18:00."
    if "precio" in text or "costo" in text:
        return "Esta es una respuesta de demostración. Aquí conectaremos el catálogo y los precios reales."
    if "contacto" in text or "persona" in text or "humano" in text:
        return "De acuerdo. Esta demostración no tiene un operador conectado todavía."
    return (
        f"Recibí tu mensaje: «{message_text[:300]}».\n"
        "Soy un agente de demostración. Escribe *ayuda* para ver lo que puedo hacer."
    )
