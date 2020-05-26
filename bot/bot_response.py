import csv
import requests
from collections import Counter

import warnings
warnings.filterwarnings("ignore")

from bot import config
from bot.model.detector import Yolo_Detector

class Bot_Response():
    def __init__(self):
        self.TOKEN = config.TOKEN
        self.URL = config.BASE_URL
        self.URL_FILES = config.FILE_URL
        self.Detector = Yolo_Detector()
        self.nutrition = {}
        with open('bot/model/nutrients.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader, None)
            for row in reader:
                self.nutrition[row[0]] = (float(row[1]), float(row[2]), 
                                          float(row[3]), float(row[4]))

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def send_message(self, text, chat_id):
        params = {"chat_id": chat_id,
                  "text": text,
                  "parse_mode": "Markdown"}
        requests.get(self.URL + "sendMessage", params=params)
    
    def send_photo(self, photo_path, chat_id):
        requests.post(self.URL + 'sendPhoto', data={'chat_id': chat_id}, 
                      files={'photo': open(photo_path, 'rb')})
    
    def process_output(self, products):
        base_nutr = "({0} fats, {1} carbohydrates, {2} proteins)"
        text = ""
        # count each type of products
        prod_counter = Counter(products)
        total = 0
        for product in prod_counter:
            energy, fat, carb, prot = self.nutrition[product]
            N = prod_counter[product]
            batch_energy = energy * N
            if total != 0:
                text += "\n"
            total += batch_energy
            text += "*" + product + " x" + str(N) + "*, {} kcal\n".format(batch_energy) + \
                    base_nutr.format(fat * N, carb * N, prot * N)
        text += "\n------\n*Total energy*: {} kcal".format(str(total))
        return text

    def message_response(self, req, updates):
        resp = []
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
            name = update["message"]["chat"]["first_name"]
            try:
                file_name = req.get_photo(update["message"])
                file_path = './data/photos' + file_name
                save_path = './data/processed' + file_name
                products = self.Detector.run_detector(file_path, save_path)
                msg = ""
                if len(products) == 0:
                    msg += "no products"
                else:
                    msg += self.process_output(products)
                    self.send_photo(save_path, chat)
                self.send_message(msg, chat)
                resp.append((chat, name, save_path, msg))
                print("Response is sent to ", chat)
            except Exception:
                self.send_message("Please send image", chat)
                resp.append((chat, name, "no_img", "no_img"))
                print("Exception is sent to ", chat)  
        return resp