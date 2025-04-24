import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os

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
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Encriptar a conexão
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, EMAIL_TO, text)
        server.quit()
        print(f"📧 E-mail enviado com sucesso para {EMAIL_TO}.")
    except Exception as e:
        print(f"⚠️ Falha no envio de e-mail: {e}")

# Função para registrar histórico
def registrar_historico(mensagem):
    with open("historico.txt", "a", encoding="utf-8") as f:
        data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{data_hora} - {mensagem}\n")

# URL do site e cabeçalhos
url = "https://www.feture.com.tw/product_list.asp"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Seleciona os blocos de produtos
product_blocks = soup.select("div.product-item")

# Mensagem inicial
print("🔍 Verificando produtos 'SOLD OUT'...\n")
historico_mensagem = "Início da verificação dos produtos."

# Registra no histórico
registrar_historico(historico_mensagem)

for block in product_blocks:
    name_tag = block.select_one("h5.title a")
    name = name_tag.get_text(strip=True) if name_tag else "Produto sem nome"

    # Verifica se tem imagem de soldout
    soldout_img = block.select_one("div.product-img img[src*='soldout.jpg']")

    if soldout_img:
        mensagem = f"❌ {name} está ESGOTADO"
        print(mensagem)
        registrar_historico(mensagem)
        # Envia o e-mail
        enviar_email("Produto Sold Out", f"O produto '{name}' está ESGOTADO no estoque.")
    else:
        mensagem = f"🟢 {name} está DISPONÍVEL"
        print(mensagem)
        registrar_historico(mensagem)

# Finaliza a verificação
print("\n✅ Verificação concluída.")
