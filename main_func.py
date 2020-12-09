#Turk Dil Kurumu scraper.
#Sitedeki tüm kelimeleri alır, .txt dosyasına yazar.

import requests
import re
import sqlite3
import json

# Database Actions
conn = sqlite3.connect('tdkscraper.db')
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS Anlamlar')
c.execute('DROP TABLE IF EXISTS Lisanlar')
c.execute('DROP TABLE IF EXISTS Turler')
c.execute('DROP TABLE IF EXISTS Kelimeler')
c.executescript('''
            CREATE TABLE IF NOT EXISTS Anlamlar(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            anlam TEXT,
            ornek TEXT,
            yazar TEXT
            );

            CREATE TABLE IF NOT EXISTS Lisanlar(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            lisan TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Turler(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            tur TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Kelimeler(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            kelime TEXT,
            tur_id INTEGER,
            lisan_id INTEGER,
            anlam_id INTEGER
            );
''')

url = 'https://sozluk.gov.tr/autocomplete.json'
uh = requests.get(url)
if not uh.status_code == 200: raise Exception('Siteye baglanilamadi :(')
fh = open('output.txt', 'w', encoding='utf-8')

# Apply filters to filter out non-word content. Set False to disable.
def stringCheck (word=str):
    filters = True 
    if filters:
        if re.search("^[a-z][a-z]", word) and len(re.findall("\s", word)) == 0: return True # Eliminate letters and white space containing stuff
        else: return False
    else: return True

# Get all of the words
data = uh.json()
wordlist = list()

for i in data:
    word = i.get('madde')
    word = word.strip()
    if stringCheck(word):
        wordlist.append(word) # append all items into a list
        #fh.write(word) # Write to output.txt
        #fh.write('\n') # Insert new line
    else: pass

for k in range(len(wordlist)):
    pick_word = wordlist[k]
    word_url = f"https://sozluk.gov.tr/gts?ara={pick_word}"
    word_uh = requests.get(word_url)
    if not word_uh.status_code == 200: raise Exception('Siteye baglanilamadi :(') 
    else: print(f"Baglanildi, {pick_word} kelimesi için {word_url} adresinden veri cekiliyor...")
    word_data = word_uh.json()

    anlam_sayisi = len(word_data)
    print(f"Bu kelimenin {anlam_sayisi} farklı anlamı var.")

    for i in range(len(word_data)):

        kelime = pick_word
        anlam = word_data[i]['anlamlarListe'][0]['anlam']
        try: ornek = word_data[i]['anlamlarListe'][0]['orneklerListe'][0]['ornek']
        except: ornek = ""
        try: yazar = word_data[i]['anlamlarListe'][0]['orneklerListe'][0]['yazar'][0]['tam_adi'] 
        except: yazar = ""
        try: tur = word_data[i]['anlamlarListe'][0]['ozelliklerListe'][0]['tam_adi']
        except: tur = ""
        try: lisan = word_data[i]['lisan']
        except: lisan = None

        c.execute('''INSERT OR IGNORE INTO Anlamlar (anlam, ornek, yazar) VALUES
         (?, ?, ?)''', (anlam, ornek, yazar ))
        c.execute('SELECT id FROM Anlamlar WHERE anlam = ? AND ornek = ? AND yazar = ? ', (anlam, ornek, yazar))
        anlam_id = c.fetchone()[0]

        c.execute('''INSERT OR IGNORE INTO Lisanlar (lisan) VALUES
         (?)''', (lisan, ))
        c.execute('SELECT id FROM Lisanlar WHERE lisan = ? ', (lisan, ))
        lisan_id = c.fetchone()[0]

        c.execute('''INSERT OR IGNORE INTO Turler (tur) VALUES
         (?)''', (tur, ))
        c.execute('SELECT id FROM Turler WHERE tur = ? ', (tur, ))
        tur_id = c.fetchone()[0]

        c.execute('''INSERT OR IGNORE INTO Kelimeler (kelime, tur_id, lisan_id, anlam_id) VALUES
         (?, ?, ?, ?)''', (kelime, tur_id, lisan_id, anlam_id ))
        
        conn.commit()

        print(kelime, anlam, ornek, yazar, tur, lisan)
       