class Game:
    def __init__(self, name, host_id):
        self.host_id = host_id
        self.users_amount = 0
        self.name = name
        self.users = []
        self.results = []
        self.status = "playing"
        self.cards = []

    def addUser(self, user):
        self.users.append(user)
        self.users_amount += 1

    def sendAllUsers(self, vk, text, random_id):
        for user in self.users:
            vk.messages.send(
                peer_id=user.user_id,
                message=text,
                random_id=random_id,
            )

class Games:
    def __init__(self, games):
        self.games = []
    def getGames(self):
        return self.games