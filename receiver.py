import serial
import threading
import time
import vgamepad as vg

# ======================================================
# CONFIGURAÇÕES
# ======================================================

PORTA_GUITARRA_BAIXO = "COM4"
PORTA_BATERIA = "COM5"

BAUD_GUITARRA_BAIXO = 115200
BAUD_BATERIA = 115200

PULSE_BATERIA = 0.004
TEMPO_INICIALIZACAO = 1.5

LOG_ATIVO = True

# ======================================================
# CONTROLES VIRTUAIS
# ======================================================

guitarra = vg.VX360Gamepad()
baixo = vg.VX360Gamepad()
bateria = vg.VX360Gamepad()

# ======================================================
# MAPA DE BOTÕES - GUITARRA E BAIXO
# ======================================================

MAPA_CORDAS = {
    "GREEN": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "RED": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "YELLOW": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "BLUE": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "ORANGE": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
}

BOTAO_STRUM = vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN

# ======================================================
# CÓDIGOS - GUITARRA
# ======================================================

CODIGOS_GUITARRA_DOWN = {
    1: "GREEN",
    2: "RED",
    3: "YELLOW",
    4: "BLUE",
    5: "ORANGE",
    6: "STRUM",
    7: "START",
}

CODIGOS_GUITARRA_UP = {
    101: "GREEN",
    102: "RED",
    103: "YELLOW",
    104: "BLUE",
    105: "ORANGE",
    106: "STRUM",
    107: "START",
}

# ======================================================
# CÓDIGOS - BAIXO
# ======================================================

CODIGOS_BAIXO_DOWN = {
    21: "GREEN",
    22: "RED",
    23: "YELLOW",
    24: "BLUE",
    25: "ORANGE",
    26: "STRUM",
    27: "START",
}

CODIGOS_BAIXO_UP = {
    121: "GREEN",
    122: "RED",
    123: "YELLOW",
    124: "BLUE",
    125: "ORANGE",
    126: "STRUM",
    127: "START",
}

# ======================================================
# MAPA DA BATERIA
# ======================================================

MAPA_BATERIA = {
    "DRUM_RED:DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "DRUM_YELLOW:DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "DRUM_BLUE:DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "DRUM_GREEN:DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "DRUM_ORANGE:DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "KICK:DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "START:DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
}

# ======================================================
# ESTADOS
# ======================================================

def criar_estado():
    return {
        "GREEN": False,
        "RED": False,
        "YELLOW": False,
        "BLUE": False,
        "ORANGE": False,
        "STRUM": False,
        "START": False,
    }


estado_guitarra = criar_estado()
estado_baixo = criar_estado()

# ======================================================
# CONTROLE DE EXECUÇÃO
# ======================================================

executando = True
lock_log = threading.Lock()

serial_guitarra_baixo = None
serial_bateria = None

# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================

def log(mensagem):
    if not LOG_ATIVO:
        return

    with lock_log:
        print(mensagem)


def pressionar_botao(nome_instrumento, gamepad, estados, botao):
    if botao not in MAPA_CORDAS:
        return

    if estados[botao]:
        return

    estados[botao] = True

    gamepad.press_button(
        button=MAPA_CORDAS[botao]
    )
    gamepad.update()

    log(f"[{nome_instrumento}] {botao}:DOWN")


def soltar_botao(nome_instrumento, gamepad, estados, botao):
    if botao not in MAPA_CORDAS:
        return

    if not estados[botao]:
        return

    estados[botao] = False

    gamepad.release_button(
        button=MAPA_CORDAS[botao]
    )
    gamepad.update()

    log(f"[{nome_instrumento}] {botao}:UP")


def pressionar_strum(nome_instrumento, gamepad, estados):
    if estados["STRUM"]:
        return

    estados["STRUM"] = True

    gamepad.press_button(
        button=BOTAO_STRUM
    )
    gamepad.update()

    log(f"[{nome_instrumento}] STRUM:DOWN")


def soltar_strum(nome_instrumento, gamepad, estados):
    if not estados["STRUM"]:
        return

    estados["STRUM"] = False

    gamepad.release_button(
        button=BOTAO_STRUM
    )
    gamepad.update()

    log(f"[{nome_instrumento}] STRUM:UP")


def processar_evento(nome_instrumento, gamepad, estados, botao, acao):
    if botao == "STRUM":
        if acao == "DOWN":
            pressionar_strum(
                nome_instrumento,
                gamepad,
                estados
            )
        else:
            soltar_strum(
                nome_instrumento,
                gamepad,
                estados
            )

        return

    if acao == "DOWN":
        pressionar_botao(
            nome_instrumento,
            gamepad,
            estados,
            botao
        )
    else:
        soltar_botao(
            nome_instrumento,
            gamepad,
            estados,
            botao
        )


def processar_codigo_guitarra_baixo(codigo):
    if codigo in CODIGOS_GUITARRA_DOWN:
        processar_evento(
            "GUITARRA",
            guitarra,
            estado_guitarra,
            CODIGOS_GUITARRA_DOWN[codigo],
            "DOWN"
        )
        return

    if codigo in CODIGOS_GUITARRA_UP:
        processar_evento(
            "GUITARRA",
            guitarra,
            estado_guitarra,
            CODIGOS_GUITARRA_UP[codigo],
            "UP"
        )
        return

    if codigo in CODIGOS_BAIXO_DOWN:
        processar_evento(
            "BAIXO",
            baixo,
            estado_baixo,
            CODIGOS_BAIXO_DOWN[codigo],
            "DOWN"
        )
        return

    if codigo in CODIGOS_BAIXO_UP:
        processar_evento(
            "BAIXO",
            baixo,
            estado_baixo,
            CODIGOS_BAIXO_UP[codigo],
            "UP"
        )
        return

    log(f"[COM4][DESCONHECIDO] Código recebido: {codigo}")


def soltar_todos_instrumento(gamepad, estados):
    for nome, botao_virtual in MAPA_CORDAS.items():
        gamepad.release_button(
            button=botao_virtual
        )
        estados[nome] = False

    gamepad.release_button(
        button=BOTAO_STRUM
    )

    estados["STRUM"] = False
    gamepad.update()


def soltar_todos_bateria():
    botoes_unicos = set(MAPA_BATERIA.values())

    for botao in botoes_unicos:
        bateria.release_button(button=botao)

    bateria.update()


def soltar_todos():
    soltar_todos_instrumento(
        guitarra,
        estado_guitarra
    )

    soltar_todos_instrumento(
        baixo,
        estado_baixo
    )

    soltar_todos_bateria()

# ======================================================
# THREAD - GUITARRA E BAIXO
# ======================================================

def ler_guitarra_baixo():
    global executando

    log(
        f"[COM4] Guitarra e baixo iniciados em "
        f"{PORTA_GUITARRA_BAIXO} @ {BAUD_GUITARRA_BAIXO}"
    )

    while executando:
        try:
            dado = serial_guitarra_baixo.read(1)

            if not dado:
                continue

            codigo = dado[0]
            processar_codigo_guitarra_baixo(codigo)

        except serial.SerialException as erro:
            if executando:
                log(f"[COM4] Erro serial: {erro}")

            executando = False
            break

        except Exception as erro:
            if executando:
                log(f"[COM4] Erro inesperado: {erro}")

# ======================================================
# THREAD - BATERIA
# ======================================================

def ler_bateria():
    global executando

    pending = []

    log(
        f"[COM5] Bateria iniciada em "
        f"{PORTA_BATERIA} @ {BAUD_BATERIA}"
    )

    while executando:
        try:
            agora = time.perf_counter()

            i = 0

            while i < len(pending):
                tempo_liberar, botao = pending[i]

                if agora >= tempo_liberar:
                    bateria.release_button(button=botao)
                    bateria.update()
                    pending.pop(i)
                else:
                    i += 1

            if serial_bateria.in_waiting:
                linha = serial_bateria.readline()

                mensagem = linha.decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not mensagem:
                    continue

                mensagem = mensagem.upper()

                botao = MAPA_BATERIA.get(mensagem)

                if botao is None:
                    log(f"[BATERIA][DESCONHECIDO] {mensagem}")
                    continue

                log(
                    f"[BATERIA] "
                    f"{time.strftime('%H:%M:%S')} "
                    f"{mensagem}"
                )

                bateria.press_button(button=botao)
                bateria.update()

                pending.append((
                    time.perf_counter() + PULSE_BATERIA,
                    botao
                ))

            time.sleep(0.0002)

        except serial.SerialException as erro:
            if executando:
                log(f"[COM5] Erro serial: {erro}")

            executando = False
            break

        except Exception as erro:
            if executando:
                log(f"[COM5] Erro inesperado: {erro}")

    for _, botao in pending:
        bateria.release_button(button=botao)

    bateria.update()

# ======================================================
# INICIALIZAÇÃO DAS PORTAS SERIAIS
# ======================================================

def abrir_portas():
    global serial_guitarra_baixo
    global serial_bateria

    try:
        serial_guitarra_baixo = serial.Serial(
            port=PORTA_GUITARRA_BAIXO,
            baudrate=BAUD_GUITARRA_BAIXO,
            timeout=0.05
        )

    except serial.SerialException as erro:
        print("")
        print("======================================")
        print(" ERRO AO ABRIR GUITARRA/BAIXO")
        print("======================================")
        print(f"Porta: {PORTA_GUITARRA_BAIXO}")
        print(f"Erro : {erro}")
        print("")
        raise SystemExit(1)

    try:
        serial_bateria = serial.Serial(
            port=PORTA_BATERIA,
            baudrate=BAUD_BATERIA,
            timeout=0.01
        )

    except serial.SerialException as erro:
        if serial_guitarra_baixo.is_open:
            serial_guitarra_baixo.close()

        print("")
        print("======================================")
        print(" ERRO AO ABRIR A BATERIA")
        print("======================================")
        print(f"Porta: {PORTA_BATERIA}")
        print(f"Erro : {erro}")
        print("")
        raise SystemExit(1)

    time.sleep(TEMPO_INICIALIZACAO)

    serial_guitarra_baixo.reset_input_buffer()
    serial_bateria.reset_input_buffer()

# ======================================================
# INFORMAÇÕES
# ======================================================

def mostrar_informacoes():
    print("")
    print("======================================")
    print(" Clone Hero - 3 Instrumentos")
    print("======================================")
    print("")
    print("Controle virtual 1 -> Guitarra")
    print("Controle virtual 2 -> Baixo")
    print("Controle virtual 3 -> Bateria")
    print("")
    print(
        f"Guitarra/Baixo: "
        f"{PORTA_GUITARRA_BAIXO} @ {BAUD_GUITARRA_BAIXO}"
    )
    print(
        f"Bateria        : "
        f"{PORTA_BATERIA} @ {BAUD_BATERIA}"
    )
    print(
        f"Logs           : "
        f"{'ATIVADOS' if LOG_ATIVO else 'DESATIVADOS'}"
    )
    print("")
    print("Pronto!")
    print("")

# ======================================================
# EXECUÇÃO
# ======================================================

abrir_portas()
mostrar_informacoes()

thread_guitarra_baixo = threading.Thread(
    target=ler_guitarra_baixo,
    daemon=True
)

thread_bateria = threading.Thread(
    target=ler_bateria,
    daemon=True
)

thread_guitarra_baixo.start()
thread_bateria.start()

try:
    while executando:
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nEncerrando...")

finally:
    executando = False

    thread_guitarra_baixo.join(timeout=1.0)
    thread_bateria.join(timeout=1.0)

    soltar_todos()

    if (
        serial_guitarra_baixo is not None
        and serial_guitarra_baixo.is_open
    ):
        serial_guitarra_baixo.close()

    if (
        serial_bateria is not None
        and serial_bateria.is_open
    ):
        serial_bateria.close()

    print("Controles liberados.")
    print("Portas seriais fechadas.")
    print("Finalizado.")
