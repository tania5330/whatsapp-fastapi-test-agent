from app.agent import build_reply

def test_greeting():
    assert "Hola" in build_reply("hola")

def test_help():
    assert "horario" in build_reply("ayuda").lower()

def test_unknown_message_is_acknowledged():
    assert "Recibí tu mensaje" in build_reply("mensaje de prueba")
