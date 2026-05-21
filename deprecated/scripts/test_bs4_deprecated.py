import requests
from bs4 import BeautifulSoup

url = 'https://enjoylearningsanskrit.com/scriptures/parashara/chapter-1'
html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')

print("Title:", soup.title.text)

# Let's see if we can find shloka containers
# Often they have class "verse" or something similar.
for div in soup.find_all('div')[:50]:
    if div.get('class'):
        print(div.get('class'))
