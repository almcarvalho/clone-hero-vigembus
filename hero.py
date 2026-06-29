"""
clonehero_vigembus_server.py

Servidor Python para receber comandos UDP de ESP32 e criar 2 controles virtuais:
- Porta UDP 5000 = GUITARRA
- Porta UDP 5001 = BATERIA

Requisitos no Windows:
1) Instale o ViGEmBus:
   https://vigembus.com/ 
   Download 

2) Instale a biblioteca Python:
   pip install vgamepad

3) Rode:
   python hero.py

Formato esperado vindo do ESP32:
GREEN:DOWN
GREEN:UP
RED:DOWN
RED:UP
...
"""

import socket
import threading
import time
import vgamepad as vg


# =============================
# CONFIGURAÇÕES UDP
# =============================

UDP_IP = "0.0.0.0"

PORTA_GUITARRA = 5000
PORTA_BATERIA = 5001

BUFFER_SIZE = 1024


# =============================
# CRIA OS CONTROLES VIRTUAIS
# =============================

guitarra = vg.VX360Gamepad()
bateria = vg.VX360Gamepad()

print("Controles virtuais criados:")
print("Controle 1: GUITARRA")
print("Controle 2: BATERIA")


# =============================
# MAPEAMENTO DA GUITARRA
# =============================
# Clone Hero pode ser configurado depois lendo esses botões no menu.

MAPA_GUITARRA = {
    "GREEN":  vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "RED":    vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "YELLOW": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "BLUE":   vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "ORANGE": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "START":  vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
}

# Palheta será simulada no D-PAD para baixo.
# Se você tiver palheta para cima e para baixo no futuro,
# crie STRUM_UP e STRUM_DOWN separados.
PALHETA_GUITARRA = "STRUM"


# =============================
# MAPEAMENTO DA BATERIA
# =============================

MAPA_BATERIA = {
    "DRUM_RED":    vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "DRUM_YELLOW": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "DRUM_BLUE":   vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "DRUM_GREEN":  vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "DRUM_ORANGE": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "KICK":        vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "START":       vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
}


# =============================
# FUNÇÕES AUXILIARES
# =============================

def apertar_botao(gamepad, botao):
    gamepad.press_button(button=botao)
    gamepad.update()


def soltar_botao(gamepad, botao):
    gamepad.release_button(button=botao)
    gamepad.update()


def palheta_down(gamepad):
    gamepad.directional_pad(direction=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
    gamepad.update()


def palheta_up(gamepad):
    gamepad.directional_pad(direction=0)
    gamepad.update()


def processar_guitarra(mensagem):
    try:
        botao, acao = mensagem.split(":")
    except ValueError:
        print("[GUITARRA] Pacote inválido:", mensagem)
        return

    botao = botao.strip().upper()
    acao = acao.strip().upper()

    if botao == PALHETA_GUITARRA:
        if acao == "DOWN":
            palheta_down(guitarra)
        elif acao == "UP":
            palheta_up(guitarra)
        return

    if botao not in MAPA_GUITARRA:
        print("[GUITARRA] Botão desconhecido:", botao)
        return

    if acao == "DOWN":
        apertar_botao(guitarra, MAPA_GUITARRA[botao])
    elif acao == "UP":
        soltar_botao(guitarra, MAPA_GUITARRA[botao])


def processar_bateria(mensagem):
    try:
        botao, acao = mensagem.split(":")
    except ValueError:
        print("[BATERIA] Pacote inválido:", mensagem)
        return

    botao = botao.strip().upper()
    acao = acao.strip().upper()

    if botao not in MAPA_BATERIA:
        print("[BATERIA] Botão desconhecido:", botao)
        return

    if acao == "DOWN":
        apertar_botao(bateria, MAPA_BATERIA[botao])
    elif acao == "UP":
        soltar_botao(bateria, MAPA_BATERIA[botao])


def servidor_udp(porta, nome, funcao_processar):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, porta))

    print(f"[{nome}] Aguardando pacotes UDP na porta {porta}...")

    while True:
        try:
            dados, endereco = sock.recvfrom(BUFFER_SIZE)
            mensagem = dados.decode("utf-8", errors="ignore").strip()

            if mensagem:
                print(f"[{nome}] {endereco} -> {mensagem}")
                funcao_processar(mensagem)

        except Exception as erro:
            print(f"[{nome}] Erro:", erro)
            time.sleep(0.1)


# =============================
# INICIA SERVIDORES
# =============================

thread_guitarra = threading.Thread(
    target=servidor_udp,
    args=(PORTA_GUITARRA, "GUITARRA", processar_guitarra),
    daemon=True
)

thread_bateria = threading.Thread(
    target=servidor_udp,
    args=(PORTA_BATERIA, "BATERIA", processar_bateria),
    daemon=True
)

thread_guitarra.start()
thread_bateria.start()

print("")
print("Servidor iniciado.")
print("Guitarra ESP32 deve enviar para UDP 5000.")
print("Bateria ESP32 deve enviar para UDP 5001.")
print("Abra o Clone Hero e configure os dois controles.")
print("Pressione CTRL+C para sair.")
print("")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Encerrando...")

    # Solta tudo ao sair
    for botao in MAPA_GUITARRA.values():
        guitarra.release_button(button=botao)

    for botao in MAPA_BATERIA.values():
        bateria.release_button(button=botao)

    guitarra.directional_pad(direction=0)
    guitarra.update()
    bateria.update()

    print("Finalizado.")
