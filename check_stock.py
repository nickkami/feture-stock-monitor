import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os
import json

# Envia e-mail com autenticação SMTP
def enviar_email(assunto, corpo_email):
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_TO = os.getenv("EMAIL_TO")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo_email, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"📧 E-mail enviado com sucesso para {EMAIL_TO}")
    except Exception as e:
        print(f"⚠️ Falha no envio de e-mail: {e}")

# Salva estado dos produtos
def salvar_estado_produtos(estado):
    with open("estado_produtos.json", "w", encoding="utf-8") as f:
        json.dump(estado, f)

# Carrega estado anterior (se existir)
def carregar_estado_produtos():
    try:
        with open("estado_produtos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Registrar log
def registrar_historico(mensagem):
    with open("historico.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - {mensagem}\n")

# Scraping
url = "https://www.feture.com.tw/product_list.asp"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
product_blocks = soup.select("div.product-item")

estado_antigo = carregar_estado_produtos()
estado_atual = {}

primeira_execucao = not bool(estado_antigo)

print("🔍 Verificando alterações nos produtos...\n")

for block in product_blocks:
    name_tag = block.select_one("h5.title a")
    name = name_tag.get_text(strip=True) if name_tag else "Produto sem nome"

    soldout_img = block.select_one("div.product-img img[src*='soldout.jpg']")
    status_atual = 'soldout' if soldout_img else 'disponivel'
    estado_atual[name] = status_atual

    status_antigo = estado_antigo.get(name)

    # Se for a primeira execução, não envia nada, só salva
    if primeira_execucao:
        continue

    # Só envia se houver mudança de status
    if status_atual != status_antigo:
        if status_atual == 'soldout':
            msg = f"❌ {name} está ESGOTADO"
            enviar_email("Produto Sold Out", f"O produto '{name}' está ESGOTADO no estoque.")
        else:
            msg = f"🟢 {name} voltou a ESTAR DISPONÍVEL"
            enviar_email("Produto Disponível", f"O produto '{name}' voltou ao estoque.")

        print(msg)
        registrar_historico(msg)

# Salvar novo estado
salvar_estado_produtos(estado_atual)

if primeira_execucao:
    print("📌 Primeira execução detectada. Estado inicial salvo sem envio de e-mails.")
else:
    print("\n✅ Verificação finalizada.")
