from shop import db, bcrypt
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username= db.Column(db.String(length=30), nullable=False, unique=True)
    email = db.Column(db.String(length=60), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=70), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=100)
    
    items = db.relationship('Item', backref='owner', lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, password_plain_text):
        self.password_hash = bcrypt.generate_password_hash(password_plain_text).decode('utf-8')

    def check_password(self, password_plain_text):
        return bcrypt.check_password_hash(self.password_hash, password_plain_text)

    def __repr__(self) -> str:
        return f"User - username: {self.username}, email: {self.email}"


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    amount = db.Column(db.Integer(), nullable=False, default=1)
    # image_src = db.Column(db.String(length=30), nullable=False)

    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f"Item - name: {self.name}, price: {self.price}$"
