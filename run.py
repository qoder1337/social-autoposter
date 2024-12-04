from app import create_app, db
from app.utils.x_post import PostOnX



app = create_app("development")

with app.app_context():
    # db.create_all()
    textinput = "FUN FACT: #Sportwetten sind cool!"
    url = "http://hallo.devo"
    x_post = PostOnX("bestinpoker", textinput, url)

    x_post.tweet()



if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=True,
        port=4444
    )
