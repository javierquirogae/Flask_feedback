from app import app
from models import db, Feedback, User


db.drop_all()
db.create_all()




# username - a unique primary key that is no longer than 20 characters.
# password - a not-nullable column that is text
# email - a not-nullable column that is unique and no longer than 50 characters.
# first_name - a not-nullable column that is no longer than 30 characters.
# last_name - a not-nullable column that is no longer than 30 characters.

user = User(
    username="jq",
    password="123",
    email="jq@fake.com",
    first_name="jav",
    last_name="Q"
)



# id - a unique primary key that is an auto incrementing integer
# title - a not-nullable column that is at most 100 characters
# content - a not-nullable column that is text
# username - a foreign key that references the username column in the users table



feedback = Feedback(
    title="I Am Title",
    content="This is me giving feedback!!",
    username="jq"
)

db.session.add(user)
db.session.commit()

db.session.add(feedback)
db.session.commit()