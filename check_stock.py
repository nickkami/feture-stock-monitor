import requests
from bs4 import BeautifulSoup

url = "https://www.feture.com.tw/product_list.asp"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

product_blocks = soup.select("div.product-item")

print("🔍 Verificando produtos 'SOLD OUT'...\n")

for block in product_blocks:
    name_tag = block.select_one("h5.title a")
    name = name_tag.get_text(strip=True) if name_tag else "Produto sem nome"

    # Verifica se tem imagem de soldout
    soldout_img = block.select_one("div.product-img img[src*='soldout.jpg']")

    if soldout_img:
        print(f"❌ {name} está ESGOTADO")
    else:
        print(f"🟢 {name} está DISPONÍVEL")

print("\n✅ Verificação concluída.")



