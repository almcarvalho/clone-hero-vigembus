import serial
import time
import vgamepad as vg

# ======================================================
# CONFIGURAÇÕES
# ======================================================

SERIAL_PORT = "COM4"
SERIAL_BAUD = 115200

LOG_ATIVO = True

# Pequena pausa usada ao iniciar a conexão Serial.
TEMPO_INICIALIZACAO = 1.5

# ======================================================
# CÓDIGOS RECEBIDOS DO ESP32
# ======================================================
#
# DOWN:
#   1 = GREEN
#   2 = RED
#   3 = YELLOW
#   4 = BLUE
#   5 = ORANGE
#   6 = STRUM
#   7 = START
#
# UP:
#   101 = GREEN
#   102 = RED
#   103 = YELLOW
#   104 = BLUE
#   105 = ORANGE
#   106 = STRUM
#   107 = START
#
# ======================================================

CODIGOS_DOWN = {
    1: "GREEN",
    2: "RED",
    3: "YELLOW",
    4: "BLUE",
    5: "ORANGE",
    6: "STRUM",
    7: "START",
}

CODIGOS_UP = {
    101: "GREEN",
    102: "RED",
    103: "YELLOW",
    104: "BLUE",
    105: "ORANGE",
    106: "STRUM",
    107: "START",
}

# ======================================================
# CONTROLE VIRTUAL
# ======================================================

guitarra = vg.VX360Gamepad()

# ======================================================
# MAPA DA GUITARRA
# ======================================================

MAPA_GUITARRA = {
    "GREEN": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "RED": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "YELLOW": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "BLUE": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "ORANGE": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
}

# ======================================================
# ESTADOS
# ======================================================

estado_botoes = {
    "GREEN": False,
    "RED": False,
    "YELLOW": False,
    "BLUE": False,
    "ORANGE": False,
    "STRUM": False,
    "START": False,
}

# ======================================================
# FUNÇÕES
# ======================================================

def log(mensagem):
    if LOG_ATIVO:
        print(mensagem)


def pressionar_botao(botao):
    """
    Pressiona um botão da guitarra virtual.
    """

    if botao not in MAPA_GUITARRA:
        return

    if estado_botoes[botao]:
        return

    estado_botoes[botao] = True

    guitarra.press_button(
        button=MAPA_GUITARRA[botao]
    )

    guitarra.update()

    log(f"[GUITARRA] {botao}:DOWN")


def soltar_botao(botao):
    """
    Solta um botão da guitarra virtual.
    """

    if botao not in MAPA_GUITARRA:
        return

    if not estado_botoes[botao]:
        return

    estado_botoes[botao] = False

    guitarra.release_button(
        button=MAPA_GUITARRA[botao]
    )

    guitarra.update()

    log(f"[GUITARRA] {botao}:UP")


def pressionar_strum():
    """
    Pressiona a palheta como D-PAD para baixo.
    """

    if estado_botoes["STRUM"]:
        return

    estado_botoes["STRUM"] = True

    guitarra.directional_pad(
        direction=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN
    )

    guitarra.update()

    log("[GUITARRA] STRUM:DOWN")


def soltar_strum():
    """
    Centraliza novamente o D-PAD.
    """

    if not estado_botoes["STRUM"]:
        return

    estado_botoes["STRUM"] = False

    guitarra.directional_pad(direction=0)
    guitarra.update()

    log("[GUITARRA] STRUM:UP")


def processar_codigo(codigo):
    """
    Processa os bytes recebidos pela Serial.
    """

    if codigo in CODIGOS_DOWN:
        botao = CODIGOS_DOWN[codigo]

        if botao == "STRUM":
            pressionar_strum()
        else:
            pressionar_botao(botao)

        return

    if codigo in CODIGOS_UP:
        botao = CODIGOS_UP[codigo]

        if botao == "STRUM":
            soltar_strum()
        else:
            soltar_botao(botao)

        return

    log(f"[DESCONHECIDO] Código recebido: {codigo}")


def soltar_todos():
    """
    Solta todos os botões ao encerrar o programa.
    """

    for nome, botao_virtual in MAPA_GUITARRA.items():
        guitarra.release_button(
            button=botao_virtual
        )

        estado_botoes[nome] = False

    guitarra.directional_pad(direction=0)
    estado_botoes["STRUM"] = False

    guitarra.update()


# ======================================================
# INICIALIZAÇÃO DA SERIAL
# ======================================================

ser = None

try:
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=SERIAL_BAUD,
        timeout=0.1
    )

    time.sleep(TEMPO_INICIALIZACAO)

    # Remove possíveis mensagens antigas armazenadas no buffer.
    ser.reset_input_buffer()

except serial.SerialException as erro:
    print("")
    print("======================================")
    print(" ERRO AO ABRIR A PORTA SERIAL")
    print("======================================")
    print(f"Porta: {SERIAL_PORT}")
    print(f"Erro : {erro}")
    print("")
    print("Verifique se:")
    print("- A porta COM está correta;")
    print("- O Monitor Serial está fechado;")
    print("- O ESP32 está conectado;")
    print("- O driver da placa está instalado.")
    print("")

    raise SystemExit(1)

# ======================================================
# INFORMAÇÕES
# ======================================================

print("")
print("======================================")
print(" Clone Hero - Guitarra ESP-NOW")
print("======================================")
print(f"Serial : {SERIAL_PORT} @ {SERIAL_BAUD}")
print(f"Logs   : {'ATIVADOS' if LOG_ATIVO else 'DESATIVADOS'}")
print("")
print("Controle virtual: Guitarra")
print("")
print("Códigos esperados:")
print("1/101   -> GREEN")
print("2/102   -> RED")
print("3/103   -> YELLOW")
print("4/104   -> BLUE")
print("5/105   -> ORANGE")
print("6/106   -> STRUM")
print("7/107   -> START")
print("")
print("Pronto!")
print("")

# ======================================================
# LOOP PRINCIPAL
# ======================================================

try:
    while True:
        dado = ser.read(1)

        if not dado:
            continue

        codigo = dado[0]

        processar_codigo(codigo)

except KeyboardInterrupt:
    print("\nEncerrando...")

except serial.SerialException as erro:
    print(f"\nErro de comunicação Serial: {erro}")

except Exception as erro:
    print(f"\nErro inesperado: {erro}")

finally:
    soltar_todos()

    if ser is not None and ser.is_open:
        ser.close()

    print("Controle liberado.")
    print("Porta Serial fechada.")
    print("Finalizado.")
