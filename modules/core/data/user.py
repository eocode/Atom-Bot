from modules.core.model.account import get_accounts

user_data = {}


class User:
    def __init__(self):
        self.market = None
        self.crypto = None
        self.pair = None
        self.platform = None
        self.speak = None


def get_user_info(cid):
    if cid in user_data:
        return user_data[cid]
    else:
        return User()


def save_user_info(cid, user):
    user_data[cid] = user


def load_validate_users():
    accounts = get_accounts()
    for account in accounts:
        user = User()
        user.market = account.current_market
        user.crypto = account.current_crypto
        user.pair = account.current_pair
        user.platform = account.current_platform
        save_user_info(account.id, user)
