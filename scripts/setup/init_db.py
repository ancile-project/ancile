from ancile_web import app, db, user_datastore

with app.app_context():
    from datetime import datetime
    user_datastore.find_or_create_role("admin")
    user_datastore.find_or_create_role("app")
    user_datastore.find_or_create_role("user")

    admin = user_datastore.create_user(email="admin", password="password")
    user = user_datastore.create_user(email="user", password="user_password")
    app = user_datastore.create_user(email="app", password="app_password")

    admin.confirmed_at = datetime.now()
    user.confirmed_at = datetime.now()
    app.confirmed_at = datetime.now()

    user_datastore.add_role_to_user(admin, "admin")
    user_datastore.add_role_to_user(user, "user")
    user_datastore.add_role_to_user(app, "app")

    db.session.commit()
