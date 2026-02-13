import requests
import sqlite3
from bs4 import BeautifulSoup

connection = sqlite3.connect("prices.db")
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        product_name TEXT,
        price REAL,
        url TEXT
    )
''')

connection.commit()

URL = "https://www.gigantti.fi/product/tietokoneet-ja-toimistotarvikkeet/tietokonetarvikkeet/hiiret-ja-nappaimistot/nappaimistot/logitech-g413-se-pelinappaimisto/480827"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}


def fetch_price():
    response = requests.get(URL, headers=HEADERS)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_element = soup.find(class_="inc-vat")
        name_tag = soup.find("h1")
        name = name_tag.get_text().strip() if name_tag else "Unknown Product"   

        if price_element:
            price_text = price_element.get_text().strip()
            price_float = float(price_text.replace("€", "").replace(",", "."))                   

            cursor.execute("INSERT INTO price_history (product_name, price, url) VALUES (?, ?, ?)", 
                (name, price_float, URL))
            connection.commit()
            print(f"Price on the website: {price_float}")
        
        print("Successfully fetched the page!")
        return soup
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return None

fetch_price()   
