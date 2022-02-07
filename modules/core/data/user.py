user_data = {}


class User:
    def __init__(self):
        self.market = None
        self.crypto = None
        self.pair = None
        self.platform = None
        self.operatives = {}


def get_user_info(cid):
    if cid in user_data:
        return user_data[cid]
    else:
        return User()


def save_user_info(cid, user):
    user_data[cid] = user
