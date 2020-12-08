#Turk Dil Kurumu crawler.
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
            post_lisan INTEGER,
            FOREIGN KEY (post_lisan) REFERENCES Kelimeler(lisan_orjin)
            );

             CREATE TABLE IF NOT EXISTS Turler(
            lisan_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            lisan_isim TEXT,
            post_lisan INTEGER,
            FOREIGN KEY (post_lisan) REFERENCES Kelimeler(lisan_orjin)
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
        if re.search("^[a-z][a-z]", word) and len(re.findall("\s", word)) == 0: # Eliminate letters and white space containing stuff
            return True
        else:
            return False
    else: return True

# Get all of the words
data = uh.json()
wordlist = list()

for i in data:
    word = i.get('madde')
    word = word.strip()
    if stringCheck(word):
        wordlist.append(word) # append all items into a list
        fh.write(word) # Write to output.txt
        fh.write('\n') # Insert new line
    else: pass
fh.close()

pick_word = wordlist[456]
word_url = f"https://sozluk.gov.tr/gts?ara={pick_word}"
word_uh = requests.get(word_url)
if not word_uh.status_code == 200: raise Exception('Siteye baglanilamadi :(') 
else: print(f"Baglanildi, {pick_word} kelimesi için {word_url} adresinden veri cekiliyor...")
word_data = word_uh.json()

print(word_data)

