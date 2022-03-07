from modules.core.model import get_settings
from modules.core.model.account import get_accounts
from datetime import datetime

user_data = {}


class User:
    def __init__(self):
        self.cid = None
        self.name = None
        self.type = None
        self.market = None
        self.crypto = None
        self.pair = None
        self.platform = None
        self.speak = False
        self.is_verified = False
        self.group = {}
        self.is_admin = False
        self.is_active = False
        self.fingerprint = None
        self.minutes = None

    def set_fingerprint(self):
        self.fingerprint = datetime.now()

    def check_if_reload(self):
        if self.fingerprint is not None:
            diff = (datetime.now() - self.fingerprint)
            self.minutes = round(diff.total_seconds() / 60, 2)
            print("Last user update: ", self.minutes, " by ", self.name, " of type ", self.type)
            if self.minutes >= 1440:
                return True
            else:
                return False
        else:
            return False


def load_user(m):
    cid = m.chat.id
    if cid in user_data:
        usr = user_data[cid]
        if usr.check_if_reload() or usr.cid is None:
            return save_user_info(cid=cid, user=load_user_data(m, cid))
        else:
            return usr
    else:
        return save_user_info(cid=cid, user=load_user_data(m, cid))


def load_user_data(m, cid):
    new_user = User()
    new_user.cid = m.chat.id
    new_user.type = m.chat.type
    usr = get_settings(cid)
    if usr is not None:
        new_user.is_verified = usr.is_verified
        new_user.is_admin = usr.is_admin
        new_user.speak = usr.speak
        new_user.is_active = True
        new_user.market = usr.current_market
        new_user.crypto = usr.current_crypto
        new_user.pair = usr.current_pair
        new_user.platform = usr.current_platform
    else:
        new_user.is_verified = False
        new_user.is_admin = False
        new_user.is_active = False
    if m.chat.type in ("group", "supergroup"):
        new_user.name = m.chat.title
        usr = get_settings(m.from_user.id)
        if usr is not None:
            verified = usr.is_verified
            is_admin = usr.is_admin
            is_active = True
        else:
            verified = False
            is_admin = False
            is_active = False
        group = {"cid": m.from_user.id, "name": m.from_user.first_name, "group": True, "verified": verified,
                 "is_admin": is_admin, "is_active": is_active}
    else:
        new_user.name = m.chat.first_name
        group = {"group": False}
    new_user.group = group
    new_user.set_fingerprint()
    return new_user


def get_user_info(cid):
    if cid in user_data:
        return user_data[cid]
    else:
        return User()


def save_user_info(cid, user):
    user_data[cid] = user
    return user_data[cid]
