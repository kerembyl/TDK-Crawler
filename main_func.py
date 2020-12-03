#Turk Dil Kurumu crawler.
#Sitedeki tüm kelimeleri alır, .txt dosyasına yazar.

import requests
import re

url = 'https://sozluk.gov.tr/autocomplete.json'
uh = requests.get(url)
if not uh.status_code == 200: raise Exception('Siteye baglanilamadi :(')
fh = open('output.txt', 'w', encoding='utf-8')

# Apply filters to filter out non-word content. Set False to disable.
filters = True 

def stringCheck (word=str):
    if filters:
        if re.search("^[a-z][a-z]",word) and not re.search("[a-z]\s", word):
            return True
        else:
            return False
    else: return True


data = uh.json()
for i in data:
    word = i.get('madde')
    if stringCheck(word):
        fh.write(word)
        fh.write('\n') # Insert new line
fh.close()


