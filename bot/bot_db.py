import sqlite3
from sqlite3 import Error

class Data_Base():
    def __init__(self, db_name="./data/bot_db.sqlite"):
        self.connection = sqlite3.connect(db_name)
    
    def create_table(self):
        cursor_obj = self.connection.cursor()       
        statement = """
        CREATE TABLE IF NOT EXISTS responses(
        id INT, 
        name TEXT,
        img_path TEXT,
        output_result TEXT);
        """
        cursor_obj.execute(statement)
        self.connection.commit()
        
    def insert(self, entities):
        cursor_obj = self.connection.cursor()
        statement = """ 
        INSERT or IGNORE INTO responses(
        id, name, img_path, output_result) 
        VALUES (?, ?, ?, ?);
        """
        cursor_obj.execute(statement, entities)
        self.connection.commit()
    
    def check_if_exist(self, user_id):
        cursor_obj = self.connection.cursor()
        statement = """
        SELECT EXISTS(SELECT 1 FROM respones WHERE id=?) 
        LIMIT 1;
        """
        check = cursor_obj.execute(statement, (user_id,))
        if check.fetchone()[0]==0:
            return 0
        return 1
        
    def print_table(self):
        cursor_obj = self.connection.cursor()
        cursor_obj.execute("SELECT * FROM responses")
        rows = cursor_obj.fetchall()
        for row in rows:
            print(row)