from python_dashing.core_modules.base import ServerBase

import random
import json

class Server(ServerBase):
    @property
    def routes(self):
        yield "number", self.number
        yield "list", self.lst

    @property
    def register_checks(self):
        yield "* * * * *", self.refresh_data

    def number(self, datastore):
        return json.dumps(datastore.retrieve("number"))

    def lst(self, datastore):
        return json.dumps(datastore.retrieve("list"))

    def refresh_data(self, time_since_last_check):
        yield "number", int(random.random() * 100)
        yield "list", [int(random.random() * 100) for _ in range(10)]
