import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import sys
from datetime import datetime, timedelta
import pyautogui
import pystray
from PIL import Image
import threading
import os
import signal

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Função para ler o arquivo de configuração
def ler_configuracao(arquivo):
    config = {}
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                if '=' in linha:
                    chave, valor = linha.strip().split('=', 1)
                    config[chave.strip()] = valor.strip()
        logging.info(f"Configurações lidas do arquivo '{arquivo}'.")
    except FileNotFoundError:
        logging.error(f"Arquivo de configuração '{arquivo}' não encontrado.")
        sys.exit(1)
    return config

# Função para verificar se estamos no horário de operação
def horario_operacao(inicio_str, fim_str):
    agora = datetime.now().time()
    inicio = datetime.strptime(inicio_str, "%H:%M").time()
    fim = datetime.strptime(fim_str, "%H:%M").time()
    return inicio <= agora <= fim

# Função para carregar a imagem do ícone
def load_image(image_path):
    """Carrega a imagem do ícone a partir do arquivo."""
    try:
        return Image.open(image_path)
    except IOError:
        logging.error(f"Não foi possível carregar a imagem do ícone '{image_path}'.")
        sys.exit(1)

def on_quit(icon, item):
    global navegador_fechado, driver
    navegador_fechado = True
    if driver:
        try:
            driver.quit()
            logging.info("WebDriver encerrado pelo ícone da bandeja.")
        except Exception as e:
            logging.error(f"Erro ao encerrar o WebDriver: {e}")
    icon.stop()
    os._exit(0)  # Força a finalização imediata do script

def start_tray_icon():
    # Caminho relativo para a imagem do ícone
    icon_path = os.path.join(os.path.dirname(__file__), 'img', 'MedPlaces-Logo.ico')
    icon_image = load_image(icon_path)
    icon = pystray.Icon("Medplaces Login", icon_image, "Medplaces Login",
                        menu=pystray.Menu(
                            pystray.MenuItem("Sair", on_quit)
                        ))
    icon.run()

# Função para verificar e recarregar a página se a div de atualização aparecer
def verificar_e_atualizar_pagina(driver):
    try:
        wait = WebDriverWait(driver, 10)
        div_atualizacao = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "bad-revision")))
        logging.info("Div de atualização detectada. Recarregando a página...")
        driver.refresh()
    except Exception:
        logging.info("Aguardando div de atualização ser concluída.")

# Ler configurações do arquivo config.txt
config = ler_configuracao('config.txt')
email = config.get('email')
senha = config.get('senha')
unidade = config.get('unidade')
login_url = config.get('login_url')
inicio_horario = config.get('inicio')
fim_horario = config.get('fim')
equipamento = config.get('equipamento')

# Verificar se email, senha, unidade, URL, horários e equipamento foram lidos corretamente
if not email or not senha or not login_url or not inicio_horario or not fim_horario or not equipamento:
    logging.error("Email, senha, URL, horários ou equipamento não fornecidos no arquivo de configuração.")
    sys.exit(1)

logging.info("Iniciando o script de automação.")
logging.info(f"Versão do Selenium: {webdriver.__version__}")

# Variável de controle para rastrear se o navegador foi fechado manualmente
navegador_fechado = False
driver = None

# Adicionar tratamento de sinal
def signal_handler(signum, frame):
    global navegador_fechado
    navegador_fechado = True
    if driver:
        try:
            driver.quit()
            logging.info("WebDriver encerrado pelo sinal de interrupção.")
        except Exception as e:
            logging.error(f"Erro ao encerrar o WebDriver: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Iniciar o ícone da bandeja do sistema em uma thread separada
tray_thread = threading.Thread(target=start_tray_icon)
tray_thread.daemon = True
tray_thread.start()

while True:
    if horario_operacao(inicio_horario, fim_horario) and not navegador_fechado:
        logging.info("Estamos dentro do horário de operação.")

        # Configurar as opções do Edge
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_experimental_option('prefs', {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })

        try:
            # Configurar o WebDriver com as opções
            driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
            logging.info("WebDriver iniciado com sucesso.")

            # Abrir o site de login
            driver.get(login_url)
            logging.info(f"Site de login '{login_url}' aberto.")

            # Esperar até que os elementos estejam presentes
            wait = WebDriverWait(driver, 60)
            logging.info("Esperando pelo campo de email...")
            email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            logging.info("Campo de email encontrado!")

            logging.info("Esperando pelo campo de senha...")
            password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            logging.info("Campo de senha encontrado!")

            logging.info("Preenchendo o campo de email...")
            email_field.send_keys(email)
            logging.info("Campo de email preenchido!")

            logging.info("Preenchendo o campo de senha...")
            password_field.send_keys(senha)
            logging.info("Campo de senha preenchido!")

            # Enviar o formulário de login
            logging.info("Enviando o formulário de login...")
            password_field.send_keys(Keys.RETURN)
            logging.info("Formulário enviado!")

            time.sleep(2)

            if equipamento.lower() == "totem":
                logging.info("Esperando pelo dropdown de unidade...")
                dropdown_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "bubble-element.Dropdown.dropdown-chevron")))
                logging.info("Dropdown encontrado!")

                logging.info("Abrindo o dropdown...")
                dropdown_button.click()
                logging.info("Dropdown aberto!")

                logging.info("Esperando pelas opções do dropdown...")
                dropdown_options = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "dropdown-choice")))

                unidade_presente = False
                for option in dropdown_options:
                    if unidade in option.text:
                        unidade_presente = True
                        logging.info(f"Selecionando a unidade: {unidade}")
                        option.click()
                        break

                if not unidade_presente:
                    logging.error(f"A unidade '{unidade}' não foi encontrada no dropdown. Verifique o nome da unidade no arquivo de configuração.")
                    driver.quit()
                    driver = None
                    sys.exit(1)
            else:
                logging.info("Equipamento configurado como 'painel', pulando seleção de unidade.")

            logging.info("Tentando entrar em modo de tela cheia com PyAutoGUI...")
            pyautogui.hotkey('f11')
            time.sleep(2)  # Aguardar um tempo para garantir que o comando seja executado
            logging.info("Entrou em modo de tela cheia.")

            logging.info("O navegador permanecerá aberto. Feche a janela do navegador para encerrar o script.")

            while horario_operacao(inicio_horario, fim_horario):
                try:
                    verificar_e_atualizar_pagina(driver)  # Verificar se a página precisa ser atualizada
                    time.sleep(2)
                except Exception as e:
                    logging.info("Navegador fechado pelo usuário.")
                    navegador_fechado = True
                    break

            logging.info("Fora do horário de operação. Encerrando o script.")

        except Exception as e:
            logging.error(f"Erro ao iniciar o WebDriver: {e}")

        finally:
            if driver:
                try:
                    driver.quit()
                    logging.info("WebDriver encerrado.")
                except Exception as e:
                    logging.error(f"Erro ao encerrar o WebDriver: {e}")
                driver = None

    else:
        logging.info("Fora do horário de operação ou navegador fechado manualmente.")

    if navegador_fechado:
        logging.info("Navegador foi fechado manualmente. Encerrando o script.")
        break

    agora = datetime.now()
