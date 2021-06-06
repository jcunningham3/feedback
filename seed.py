from app import app
from models import Feedback, Users, db

#drop and create tables
db.drop_all()
db.create_all()
