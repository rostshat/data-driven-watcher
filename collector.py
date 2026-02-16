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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

connection.commit()

ITEMS_TO_WATCH = [
    "https://www.gigantti.fi/product/tietokoneet-ja-toimistotarvikkeet/tietokonetarvikkeet/hiiret-ja-nappaimistot/nappaimistot/logitech-g413-se-pelinappaimisto/480827",
    "https://www.gigantti.fi/product/tietokoneet-ja-toimistotarvikkeet/tietokonetarvikkeet/hiiret-ja-nappaimistot/nappaimistot/logitech-g915-x-lightspeed-wireless-tactile-pelinappaimisto-musta/814812",
    "https://www.gigantti.fi/product/tietokoneet-ja-toimistotarvikkeet/tietokonetarvikkeet/hiiret-ja-nappaimistot/nappaimistot/logitech-g915-x-lightspeed-wireless-clicky-pelinappaimisto-musta/814815",
    "https://www.gigantti.fi/product/tietokoneet-ja-toimistotarvikkeet/tietokonetarvikkeet/hiiret-ja-nappaimistot/nappaimistot/asus-rog-strix-scope-ii-96-pelinappaimisto-musta/764533"
]

def fetch_prices(items):
    for item in items:
        response = requests.get(item, headers=HEADERS)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Name and price parcing
            name_tag = soup.find("h1")
            name = name_tag.get_text().strip() if name_tag else "Unknown Product"   
            price_element = soup.find(class_="inc-vat")
            
            # Last Price catcher
            cursor.execute("""
            SELECT price FROM price_history 
            WHERE product_name = ? 
            ORDER BY timestamp DESC LIMIT 1
            """, (name,))

            last_record = cursor.fetchone()
            #print(f"last price for tracking: {last_record}")            

            # Price element floating and database record creation
            if price_element:
                price_text = price_element.get_text().strip()
                price_float = float(price_text.replace("€", "").replace(",", "."))                   

                cursor.execute("INSERT INTO price_history (product_name, price, url) VALUES (?, ?, ?)", 
                    (name, price_float, item))
                connection.commit()                                        

            print(f"Product name {name}")
            print(f"Price on the website: {price_float} €")
            # Price comparsion
            if last_record :
                old_price = last_record[0]

                if price_float < old_price:
                    diff = old_price - price_float
                    print(f"🔥 ЦЕНА УПАЛА! Скидка: {diff:.2f}€")
                elif price_float > old_price:
                    diff = price_float - old_price
                    print(f"📈 Цена выросла на {diff:.2f}€")
                else:
                    print("➖ Цена не изменилась.")
            else:
                print("🆕 Это новый товар, начинаем отслеживание.")  
                            
        else:
            print(f"Failed to fetch page. Status code: {response.status_code}")

fetch_prices(ITEMS_TO_WATCH)   
