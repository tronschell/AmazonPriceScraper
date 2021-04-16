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

itemName = soup.find(
    "span", attrs={'id': 'productTitle'}).string.strip()

# Exception handling for if the link doesnt include a /dp/ in it and/or if there is not /ref.
# Also found a piece of code online for making sure the ASIN is a set of numbers and letters with no symbols.

try:
    splitHere = url.split("/dp/")[1]
    itemAsin = splitHere.split("/ref")[0]
    itemAsin = splitHere.split("/ref=")[0]
    itemAsin = itemAsin[0:10]

except:
    splitHere = url.split("/product/")[1]
    itemAsin = splitHere.split("/ref")[0]
    itemAsin = splitHere.split("/ref=")[0]
    itemAsin = itemAsin[0:10]

#Test case 1, showing that the splitting works and the item ASIN can be successfully saved into the database later.
print(itemAsin)

# Exception handling for if the listing has a different price blocks
try:
    itemPrice = soup.find(
        "span", attrs={'id': 'priceblock_ourprice'}).string.strip()
except AttributeError:
    itemPrice = soup.find(
        "span", attrs={'id': 'price_inside_buybox'}).string.strip()
except:
    itemPrice = soup.find(
        "span", attrs={'id': 'newBuyBoxPrice'}).string.strip()

if listTables() == []:
    makeTable()
    print("Looks like there is no tables in this database. Creating one now...")
    print("Products table created!")
else:
    pass

print(listContent())

dt_string = now.strftime("%m/%d/%Y]")

data = (itemAsin, itemPrice, dt_string)

insertTable(data)

finalLst = minMaxAvg(itemAsin)

# Test Case 2, showing that all of the outputs from the database works.
print(f"""
+========================================================================================================================+
{itemName}  |  ASIN : {itemAsin}
        Minimum : ${finalLst[0]}  |  Maximum : ${finalLst[0]}  |  Average Price : ${finalLst[2]}  |  Current Price  :  {itemPrice}
+========================================================================================================================+""")
