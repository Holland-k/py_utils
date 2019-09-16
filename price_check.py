import requests
from bs4 import BeautifulSoup
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import datetime
import os
import time

### Todo:
###   (1) Check multiple products by reading in from a file
###       various URLs
###   (2) Figure out why the header was not working
###   (3) Do a more intelligent price comparison
URL_list = [
    'https://www.amazon.com/EVGA-GeForce-Gaming-Graphics-11G-P4-2487-KR/dp/B07KVKRLG2/ref=sr_1_1?keywords=rtx+2080+ti&qid=1568223702&s=gateway&sr=8-1',
    'https://www.amazon.com/gp/product/B00P7TPYDM/ref=ox_sc_saved_title_2?smid=ATVPDKIKX0DER&psc=1'
]

headers = { "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}

dir_prefix = "history/"
### Pull the price from the URL, specific to that URL for now. Save
### the price to the log file, and then email if it is the lowest
### price seen so far.
def get_price(URL):
    #page = requests.get(URL,headers=headers)
    page = requests.get(URL)
    while(page.status_code != 200):
        time.sleep(5)
        page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    title = soup.find(id="productTitle").get_text().strip()
    stitle = short_title(title)

    pr = soup.find(id="priceblock_ourprice")
    i = 0
    while(pr == None and i < 5):
         page = requests.get(URL, headers=headers)
         soup = BeautifulSoup(page.text, 'html.parser')
         soup.find(id="priceblock_ourprice")
         i += 1
         time.sleep(2)
         
    try:
        price = pr.get_text().strip()
    except:
        pass
    else:
        nprice = float(((price.replace('$','')).replace(',',''))[0:-3])

        if(check_price(stitle, nprice)):
            email_price(stitle, nprice, URL)
            save_price(stitle, nprice)

### Checking price history to see if today's price is the lowest,
### ignoring date field for now
def check_price(title, price):
    f = open(dir_prefix+title, 'r')
    min = -1
    for i in f:
        cp = float(i.split('\t')[1])
        if(min == -1):
            min = cp
        elif(min > cp):
            min = cp
    if(float(price) < float(min)):
        return True
    else:
        return False
        
def short_title(ltitle):
    if(len(ltitle) > 20):
        return ltitle[0:20]

### Saves the price to a text file for record keeping
### format is <date>TAB<price>; title is already in the file name
def save_price(title, price):
    try:
        f = open(dir_prefix+title, 'a')
    except:
        print("error opening file " + title)
        pass
    else:
        t = datetime.datetime.now()
        line = str(t.month) + "/" + str(t.day) + "/" + str(t.year)
        line = line + '\t' + str(price) + '\n'
        f.write(line)
        f.close()

def email_price(title, price, URL):
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

for i in URL_list:
    get_price(i)
