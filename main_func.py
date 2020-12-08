#Turk Dil Kurumu scraper.
#Sitedeki tüm kelimeleri alır, .txt dosyasına yazar.

import requests

import re
import sqlite3
import json

# Database Actions
conn = sqlite3.connect('tdkcrawler.db')
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS Anlamlar')
c.execute('DROP TABLE IF EXISTS Lisanlar')
c.execute('DROP TABLE IF EXISTS Turler')
c.executescript('''
            CREATE TABLE IF NOT EXISTS Anlamlar(
            anlam_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            anlam_metin TEXT UNIQUE,
            anlam_ornek TEXT,
            anlam_kelime TEXT NOT NULL,
            anlam_tur INTEGER,
            anlam_lisan INTEGER,
            anlam_yazar TEXT
            );

            CREATE TABLE IF NOT EXISTS Lisanlar(
            lisan_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            lisan_isim TEXT,
            FOREIGN KEY (lisan_isim) REFERENCES Anlamlar(anlam_lisan)
            );

            CREATE TABLE IF NOT EXISTS Turler(
            tur_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            tur_isim TEXT,
            FOREIGN KEY (tur_isim) REFERENCES Anlamlar(anlam_tur)
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

        anlam_kelime = pick_word
        anlam_metin = word_data[i]['anlamlarListe'][0]['anlam']
        try: anlam_ornek = word_data[i]['anlamlarListe'][0]['orneklerListe'][0]['ornek']
        except: anlam_ornek = ""
        try: anlam_yazar = word_data[i]['anlamlarListe'][0]['orneklerListe'][0]['yazar'][0]['tam_adi'] 
        except: anlam_yazar = ""
        try: anlam_tur = word_data[i]['anlamlarListe'][0]['ozelliklerListe'][0]['tam_adi']
        except: anlam_tur = ""
        try: post_lisan = word_data[i]['lisan']
        except: post_lisan = ""
        print(anlam_kelime, anlam_metin, anlam_ornek, anlam_yazar, anlam_tur, post_lisan)
        combined = (f"{anlam_kelime}, {anlam_metin}, {anlam_ornek}, {anlam_yazar}, {anlam_tur}, {post_lisan}")
        fh.write(combined) # Write to output.txt
        fh.write('\n')

fh.close()