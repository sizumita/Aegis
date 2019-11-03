from gino import Gino, GinoEngine

db = Gino()


class CommandPermission(db.Model):
    __tablename__ = 'permission'
    number = db.Column(db.Integer, autoincrement=True, primary_key=True)
    id = db.Column(db.BigInteger)
    name = db.Column(db.String(100))
    roles = db.Column(db.String(2000), default='')  # 使えるroleのリスト、,で区切る
    users = db.Column(db.String(2000), default='')  # 使えるuserのリスト、,で区切る
    permissions = db.Column(db.String(2000), default='')  # 使える権限のリスト、,で区切る
