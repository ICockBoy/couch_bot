import json


class DataBase:
    data = None

    def __init__(self):
        with open("Database/users.json", 'r') as _:
            self.data: dict[str: list] = json.load(_)

    def addUserId(self, userId: str):
        temp: set = {*self.data["userId"]}
        temp.add(userId)
        self.data["userId"] = list(temp)
        self.__save()

    def getUserIds(self) -> list[str]:
        return self.data["userId"]

    def __save(self):
        with open('Database/users.json', 'w') as _:
            json.dump(self.data, _)
