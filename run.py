from app import create_app, db

app = create_app("development")

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=True,
        port=4444
        #  threaded=False
    )
