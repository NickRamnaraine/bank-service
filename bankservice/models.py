from flask_sqlalchemy import SQLAlchemy

# Creating db
db = SQLAlchemy()

# Table that is many-to-many for transfers of money
transfer_users = db.Table(
    'transfer_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('transfer_id', db.Integer, db.ForeignKey('transfer.id'), primary_key=True)
)


# Creating User class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    accounts = db.relationship('AccountInformation', backref='user', lazy=True)


# Creating account information class that holds necessary actions for a bank
class AccountInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(25), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    account_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deposits = db.relationship('Deposit', backref='account', lazy=True)
    withdraws = db.relationship('Withdraw', backref='account', lazy=True)
    transfers = db.relationship('Transfer', backref='account', lazy=True)


# Creating deposit for bank
class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    account_id = db.Column(db.Integer, db.ForeignKey('account_information.id'), nullable=False)


# Creating withdraw for bank
class Withdraw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    account_id = db.Column(db.Integer, db.ForeignKey('account_information.id'), nullable=False)


# Creating transfers for the bank
class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    from_account_id = db.Column(db.Integer, db.ForeignKey('account_information.id'), nullable=False)
    to_account_id = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', secondary=transfer_users, backref=db.backref('transfers', lazy=True))
