import time

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
    journey = {}

    needs_update = False
    delayed_journeys = []

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
                if line == 'X' or line == 'exit':
                    break
                self.journey[line] = "Good Service"
            data = json.dumps({
                "Username": self.username,
                "Password": self.password,
                "Email": self.email,
                "Journey": self.journey
            })
            json.dump(data, f)
            print("Preferences saved")

    def get_service_updates(self):
        URL = "https://tfl.gov.uk/tube-dlr-overground/status/"

        headers = {"User-Agent":
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                       'Chrome/77.0.3865.90 Safari/537.36'}

        page = requests.get(URL, headers=headers)
        html = BeautifulSoup(page.content, 'html.parser')
        line_table = html.find(id="rainbow-list-tube-dlr-overground-tflrail-tram")

        for line in line_table.findAll('li'):
            if line in self.journey:
                if len(line['class']) > 2 and self.journey[line] == "Good Service":
                    self.journey[line] = line['class'][2].capitalize()
                    self.needs_update = True
                elif len(line['class']) == 2 and self.journey[line] != "Good Service":
                    self.journey[line] = 'Good Service'

    def send_mail(self):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(self.username, self.password)

        subject = 'Delays on your journey'

        delayed_lines = []
        for line in self.journey:
            if self.journey[line] != "Good Service":
                delayed_lines.append(line)

        body = 'There are delays on the {} lines'.format(', '.join(delayed_lines))

        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(self.username,
                        self.email,
                        message)
        print('message sent')
        self.needs_update = False
        server.quit()

    def run(self):
        self.get_service_updates()
        if self.needs_update:
            self.send_mail()
        time.sleep(900)


if __name__ == "__main__":
    tfl_updater = tflUpdater()
    tfl_updater.get_user_prefs()
    tfl_updater.run()
