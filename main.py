import requests
import smtplib
from bs4 import BeautifulSoup

URL = "https://tfl.gov.uk/tube-dlr-overground/status/"

headers ={"User-Agent":
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

page = requests.get(URL, headers=headers)

html = BeautifulSoup(page.content, 'html.parser')

train = html.find(id="rainbow-list-tube-dlr-overground-tflrail-tram")
lines = {}
for line in train.findAll('li'):
    if len(line['class']) > 2:
        lines[line['class'][1].capitalize()] = line['class'][2].capitalize()

    else:
        lines[line['class'][1].capitalize()] = 'Good Service'


