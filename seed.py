from app import app
from models import db, Tweet, User


db.drop_all()
db.create_all()



user = User(
    username="me",
    password="123"
)

tweet = Tweet(
    text="many words",
    user_id=1
)

db.session.add(user)
db.session.commit()

db.session.add(tweet)
db.session.commit()