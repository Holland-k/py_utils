import requests
from bs4 import BeautifulSoup
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import datetime
import os

URL = 'https://www.amazon.com/EVGA-GeForce-Gaming-Graphics-11G-P4-2487-KR/dp/B07KVKRLG2/ref=sr_1_1?keywords=rtx+2080+ti&qid=1568223702&s=gateway&sr=8-1'

headers = { "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}

def get_price():
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')

    #print(soup)

    title = soup.find(id="productTitle").get_text().strip()
    stitle = short_title(title)

    price = soup.find(id="priceblock_ourprice").get_text().strip()
    #print("Product title is: " + title)
    #print("Price is: " + price)
    nprice = float(((price.replace('$','')).replace(',',''))[0:-3])
    #print(nprice)

    save_price(stitle, nprice)
    if(check_price(stitle, nprice)):
        email_price(stitle, nprice)

def check_price(title, price):
    f = open("history/"+title, 'r')
    min = -1
    for i in f:
        cp = float(i.split('\t')[1])
        if(min == -1):
            min = cp
        elif(min > cp):
            min = cp
    if(price < cp):
        return True
    else:
        return False
        
def short_title(ltitle):
    if(len(ltitle) > 20):
        return ltitle[0:20]

### Saves the price to a text file for record keeping
### format is <date> <price>; title is already in the file name
def save_price(title, price):
    try:
        f = open("history/"+title, 'a')
    #except FileExistsError:
    #    f = open("history/"+title, 'a')
    except:
        print("error opening file")
        pass
    else:
        t = datetime.datetime.now()
        line = str(t.month) + "/" + str(t.day) + "/" + str(t.year)
        line = line + '\t' + str(price) + '\n'
        f.write(line)
        f.close()

def email_price(title, price):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    email = get_name()
    passw = get_pword()
    server.login(email,passw)

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = 'Price Alert on ' + title
    body = title + ' hit a new low price of ' + str(price) + ' check it out at ' + URL
    msg.attach(MIMEText(body))
    

    server.sendmail(
        email,
        email,
        msg.as_string()
    )

    print("email sent")

    server.quit()

### price_config has two lines, fist line is just the email address
### used as login, and second line is the password for that account
def get_name():
    f = open("price_config", 'r')
    name = f.readline()
    f.close()
    return name[0:-1]

def get_pword():
    f = open("price_config", 'r')
    f.readline()
    passw = f.readline()
    f.close()
    return passw[0:-1]

get_price()
