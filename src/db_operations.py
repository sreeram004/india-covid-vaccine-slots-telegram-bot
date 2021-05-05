from tinydb import TinyDB, Query

DB_PATH = "DATA.json"
TABLE_NAME = "users"

class BotDB:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.table = self.db.table(TABLE_NAME)
    
    def _get_all_data(self):
        return self.table.all()
    
    def _insert(self, data):
        if len(self._get_item(data['chat_id'])) == 0:
            self.table.insert(data)
            return True
        return False
    
    def _delete(self, chat_id):
        self.table.remove(Query().chat_id == chat_id)
        
    def _get_item(self, chat_id):
        return self.table.search(Query().chat_id == chat_id)
    
    