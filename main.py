import time

from bot.bot_response import Bot_Response
from bot.bot_requests import Bot_Requests
from bot.bot_db import Data_Base

def main():    
    Response = Bot_Response()
    Requests = Bot_Requests()
    DB = Data_Base()
    DB.create_table()
    
    last_id = None
    while True:
        print("getting updates")
        updates = Requests.get_updates(last_id)
        if len(updates["result"]) > 0:
            last_id = Requests.get_last_update_id(updates) + 1
            entities = Response.message_response(Requests, 
                                                 updates)
            for entity in entities: 
                DB.insert(entity)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
    