from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

db = SQLAlchemy()

metadata = MetaData()

class img_path(db.Model):
    __table__ = MetaData.tables['img_path_data']

class customer(db.Model):
    __table__ = MetaData.tables['customer']

