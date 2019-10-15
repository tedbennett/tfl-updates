import requests
import smtplib
from bs4 import BeautifulSoup
import json
import os


class tflUpdater():
    lines = {}
    filename = "prefs.json"

    username = ""
    password = ""
    email = ""
    journey = []

    def get_user_prefs(self):

        if os.path.exists(self.filename):
            f = open(self.filename, 'r')
            prefs = json.loads(json.load(f))
            self.username = prefs['Username']
            self.password = prefs['Password']
            self.email = prefs['Email']
            self.journey = prefs['Journey']
            print("Preferences loaded")

        else:
            f = open(self.filename, 'w')
            self.username = input("Enter your origin email address:")
            self.password = input("Enter your application password:")
            self.email = input("Enter your destination email address:")

            finished = False
            print("Enter the routes of your journey.")
            print("Enter X to exit")
            while not finished:
                line = input().title()
                if line == 'X':
                    break
                self.journey.append(line)
            data = json.dumps({
                "Username": self.username,
                "Password": self.password,
                "Email": self.email,
                "Journey": list(set(self.journey))
            })
            json.dump(data, f)
            print("Preferences saved")

    def get_service_updates(self):
        URL = "https://tfl.gov.uk/tube-dlr-overground/status/"

        headers ={"User-Agent":
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

        page = requests.get(URL, headers=headers)
        html = BeautifulSoup(page.content, 'html.parser')
        line_table = html.find(id="rainbow-list-tube-dlr-overground-tflrail-tram")

        for line in line_table.findAll('li'):
            if len(line['class']) > 2:
                self.lines[line['class'][1].capitalize()] = line['class'][2].capitalize()
            else:
                self.lines[line['class'][1].capitalize()] = 'Good Service'

    def send_mail(self):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(self.username, self.password)

        subject = 'Delays on your journey'

        body = 'There are delays on the {} lines'.format(', '.join(self.delayed_lines))

        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(self.username,
                        self.email,
                        message)
        print('message sent')
        server.quit()


if __name__ == "__main__":
    delays = ["Central"]
    tfl_updater = tflUpdater()
    tfl_updater.get_user_prefs()
    tfl_updater.get_service_updates()
    tfl_updater.send_mail(delays)
