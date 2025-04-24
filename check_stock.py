import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os
import json

# Função para enviar e-mail
def enviar_email(assunto, corpo_email):
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_TO = os.getenv("EMAIL_TO")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Configuração do e-mail
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo_email, 'plain'))

    # Envio do e-mail
    try:
        # Conectar ao servidor SMTP para cada envio
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Encriptar a conexão
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_FROM, EMAIL_TO, text)
            print(f"📧 E-mail enviado com sucesso para {EMAIL_TO}.")
    except Exception as e:
        print(f"⚠️ Falha no envio de e-mail: {e}")

# Função para registrar histórico
def registrar_historico(mensagem):
    with open("historico.txt", "a", encoding="utf-8") as f:
        data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{data_hora} - {mensagem}\n")

# Função para salvar o estado dos produtos
def salvar_estado_produtos(estado_produtos):
    with open("estado_produtos.json", "w", encoding="utf-8") as f:
        json.dump(estado_produtos, f)

# Função para carregar o estado dos produtos
def carregar_estado_produtos():
    try:
        with open("estado_produtos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Carregar o estado atual dos produtos armazenado
estado_antigo = carregar_estado_produtos()

# URL do site e cabeçalhos
url = "https://www.feture.com.tw/product_list.asp"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Seleciona os blocos de produtos
product_blocks = soup.select("div.product-item")

# Inicializa um dicionário para armazenar o novo estado dos produtos
estado_atual = {}

# Mensagem inicial
print("🔍 Verificando produtos 'SOLD OUT'...\n")

for block in product_blocks:
    name_tag = block.select_one("h5.title a")
    name = name_tag.get_text(strip=True) if name_tag else "Produto sem nome"

    # Verifica se tem imagem de soldout
    soldout_img = block.select_one("div.product-img img[src*='soldout.jpg']")

    # Estado atual do produto
    estado_atual[name] = 'soldout' if soldout_img else 'disponivel'

    if estado_antigo.get(name) != estado_atual[name]:
        # Se o estado do produto mudou, envia o e-mail
        if estado_atual[name] == 'soldout':
            mensagem = f"❌ {name} está ESGOTADO"
            print(mensagem)
            enviar_email("Produto Sold Out", f"O produto '{name}' está ESGOTADO no estoque.")
        elif estado_atual[name] == 'disponivel':
            mensagem = f"🟢 {name} voltou a ESTAR DISPONÍVEL"
            print(mensagem)
            enviar_email("Produto Disponível", f"O produto '{name}' voltou ao estoque.")
        
        # Atualiza o histórico
        registrar_historico(mensagem)

# Salva o estado atualizado dos produtos
salvar_estado_produtos(estado_atual)

# Finaliza a verificação
print("\n✅ Verificação concluída.")
