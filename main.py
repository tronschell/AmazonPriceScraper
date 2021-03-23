from bs4 import BeautifulSoup
import requests
import sqlite3
from datetime import datetime

now = datetime.now()

# Makes a table in the database


def makeTable():
    conn = sqlite3.connect('test5.db')
    print("Opened Database")

    conn.execute('''CREATE TABLE products
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ASIN INTEGER NOT NULL,
            PRICE REAL NOT NULL,
            DATE DATETIME NOT NULL);''')

    conn.close()

# Insert things into the database


def insertTable(data):
    conn = sqlite3.connect('test5.db')
    print("Opened DB")

    sql = '''INSERT INTO products(ASIN, PRICE, DATE) VALUES(?,?,?);'''

    cursor = conn.cursor()
    cursor.execute(sql, data)

    conn.commit()
    conn.close()

# List the entire contents of the database


def listContent():
    lst = []
    con = sqlite3.connect('test5.db')
    cursor = con.cursor()
    cursor.execute('''SELECT * FROM products;''')

    rows = cursor.fetchall()

    for row in rows:
        lst.append(str(row))

    return lst

# List all of the tables for debugging purposes


def listTables():
    con = sqlite3.connect('test5.db')
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return (cursor.fetchall())

# Function for finding the minimum, maximum, and average price data based on the ASIN provided


def minMaxAvg(asin):
    lst = []
    avg = 0
    count = 0
    added = 0
    con = sqlite3.connect('test5.db')
    cursor = con.cursor()
    cursor.execute('''SELECT PRICE FROM products WHERE ASIN=?;''', [asin])

    rows = cursor.fetchall()

    for row in rows:
        p = (str(row))
        newp = p.split("'")[1]
        newnewp = newp.split("$")[1]
        lst.append(float(newnewp))
        lst.sort()

        count += 1

    for x in range(len(lst)):
        added += lst[int(x)]

    avg = (added)/count
    mn = lst[0]
    mx = lst[len(lst)-1]

    return(mn, mx, avg)


# Required so Amazon doesnt FREAK OUT and think we're a bot.
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

url = input('Insert the Amazon URL: ')

req = requests.get(url, headers=HEADERS)
soup = BeautifulSoup(req.text, "html.parser")

itemName = soup.find("span", attrs={'id': 'productTitle'}).string.strip()

# Exception handling for if the link doesnt include a /dp/ in it and/or if there is not /ref.
try:
    splitHere = url.split("/dp/")[1]
    itemAsin = splitHere.split("/ref=")[0]
except AttributeError:
    itemAsin = splitHere.split("?")[0]
except IndexError:
    splitHere = url.split("/product/")[1]
    itemAsin = splitHere.split("/ref=")[0]
    try:
        itemAsin = splitHere.split("?")[0]
    except AttributeError:
        itemAsin = 0

# Exception handling for if the listing has a "dealprice" instead of a "ourprice"
try:
    itemPrice = soup.find(
        "span", attrs={'id': 'priceblock_ourprice'}).string.strip()
except AttributeError:
    itemPrice = soup.find(
        "span", attrs={'id': 'priceblock_dealprice'}).string.strip()

if listTables() == []:
    makeTable()
    print("Looks like there is no tables in this database. Creating one now...")
    print("Products table created!")
else:
    pass

dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

data_1 = (itemAsin, itemPrice, dt_string)

insertTable(data_1)
# Since data is returned as a list from the minMaxAvg() function, we need to add data to individual variables before we call them in the formatted string.
finalLst = minMaxAvg(itemAsin)
Minimum = finalLst[0]
Maximum = finalLst[1]
Average = finalLst[2]


print(f"""
+========================================================================================================================+
{itemName}  |  ASIN : {itemAsin}               
        Minimum : ${finalLst[0]}  |  Maximum : ${Maximum}  |  Average Price : ${Average}  |  Current Price  :  {itemPrice}
+========================================================================================================================+""")
