#Turk Dil Kurumu crawler.
#Sitedeki tüm kelimeleri alır, .txt dosyasına yazar.
import requests
import os

url = 'https://sozluk.gov.tr/autocomplete.json'
uh = requests.get(url)
fh = open('output.txt', 'w', encoding='utf-8')
if not uh.status_code == 200: raise Exception('Siteye baglanilamadi :(')

data = uh.json()
for i in data:
    word = i.get('madde')
    
    fh.write(word)
    fh.write('\n')

fh.close()