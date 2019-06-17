from app import app,db,user_datastore
from flask_security.confirmable import generate_confirmation_link

with app.app_context():
  user_datastore.find_or_create_role("admin")
  user_datastore.find_or_create_role("app")
  user_datastore.find_or_create_role("user")

  user = user_datastore.create_user(email='crose@vassar.edu', password='password')
  user_datastore.add_role_to_user(user, "admin")
  print(generate_confirmation_link(user))

  db.session.commit()
