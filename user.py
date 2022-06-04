class User:
    def __init__(self, name, user_id):
        self.user_id = user_id
        self.name = name
        self.game_id = -1
        self.ready = False
        self.rating = 0 
        self.true_card = ""