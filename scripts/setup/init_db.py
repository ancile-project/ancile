from app import app, db, user_datastore

with app.app_context():
  user_datastore.find_or_create_role("admin")
  user_datastore.find_or_create_role("app")
  user_datastore.find_or_create_role("user")

  db.session.commit()
