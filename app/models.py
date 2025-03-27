from . import db, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    senha_hash = db.Column(db.String(500), nullable=False)

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)
