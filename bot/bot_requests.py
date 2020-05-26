import os
import json 
import requests
import urllib

from bot import config

class Bot_Requests():
    def __init__(self):
        self.TOKEN = config.TOKEN
        self.URL = config.BASE_URL
        self.URL_FILES = config.FILE_URL
    
    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return (text, chat_id)

    def get_updates(self, offset=None):
        url = self.URL + "getUpdates?timeout=100"
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def get_photo(self, updates):
        try:      
            file_id = updates["photo"][-1]["file_id"]
            URL_to_file = self.URL + "getFile?file_id=" + file_id
            file_info = self.get_json_from_url(URL_to_file)
            file_name = file_info["result"]["file_path"]
            file_URL = self.URL_FILES + self.TOKEN + "/" + file_name
            if not os.path.isdir("./data/photos"):
                os.makedirs("./data/photos")
            # Download photo to specific folder on machine
            file_path = "./data/" + file_name
            urllib.request.urlretrieve(file_URL, file_path)
            # this returns file name without "/photos"
            return file_name[6:]
        except Exception:
            print("No photo")