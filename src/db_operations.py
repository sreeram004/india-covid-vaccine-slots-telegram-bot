from tinydb import TinyDB, Query
from pathlib import Path

data_path = Path(__file__).parent / "data"

USERS_DB_PATH = data_path / "DATA.json"
USERS_TABLE_NAME = "users"
STATES_DB_PATH = data_path / "STATES.json"
STATES_TABLE_NAME = "states"
DISTRICT_DB_PATH = data_path / "DISTRICTS.json"
DISTRICT_TABLE_NAME = "districts"


class BotDB:
    def __init__(self):
        self.db = TinyDB(USERS_DB_PATH)
        self.table = self.db.table(USERS_TABLE_NAME)

    def get_all_data(self):
        return self.table.all()

    def insert(self, data):
        if len(self._get_item(data['chat_id'])) == 0:
            self.table.insert(data)
            return True
        return False

    def delete(self, chat_id):
        self.table.remove(Query().chat_id == chat_id)

    def _get_item(self, chat_id):
        return self.table.search(Query().chat_id == chat_id)


class StateDB:
    def __init__(self):
        self.db = TinyDB(STATES_DB_PATH)
        self.state_table = self.db.table(STATES_TABLE_NAME)

    def get_states(self):
        return self.state_table.all()


class DistrictDB:
    def __init__(self):
        self.db = TinyDB(DISTRICT_DB_PATH)
        self.dist_table = self.db.table(DISTRICT_TABLE_NAME)

    def get_districts(self, state_id):
        return self.dist_table.search(Query().state_id == state_id)
