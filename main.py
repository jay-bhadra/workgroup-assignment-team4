from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

ocl_pw = r'Group3!'
#pub_ip = r"35.198.145.47"
pub_ip = r"34.140.36.224"
dbname = r"devappscloud"
project_id = r"elevated-creek-351619"
instance_name = r"devapps-cloud"
db_port = "3306"

app.config["SECRET_KEY"] = "this is not secret, remember, change it!"

db_url = f"mysql+pymysql://root:{ocl_pw}@{pub_ip}:{db_port}/{dbname}" #TCP

engine = create_engine(db_url)

@app.route("/")
def index():
    if "username" in session:
        query = f"""
        SELECT id, username, picture
        FROM users
        WHERE id!={session['user_id']}
        """
    
        with engine.connect() as connection:
            users = connection.execute(query)
    
            return render_template("users.html", users=users)
            
    else:
        return render_template("index.html")
    

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def handle_register():
    username=request.form["username"]
    password=request.form["password"]
    picture=request.form["picture"]

    hashed_password = generate_password_hash(password)

    insert_query = f"""
    INSERT INTO users(username, picture, password)
    VALUES ('{username}', '{picture}', '{hashed_password}')
    """
    with engine.connect() as connection:
        connection.execute(insert_query)
    
    follow_query = f"""
    SELECT id
    FROM users
    WHERE username='{username}'
    """
    with engine.connect() as connection:
        follower_id = connection.execute(follow_query).fetchone()
    
    follower_id = follower_id[0]
    
    insert_follower_query = f"""
    INSERT INTO follows(follower_id, followee_id)
    VALUES ('{follower_id}', '{follower_id}')
    """    
    with engine.connect() as connection:
        connection.execute(insert_follower_query)

        return redirect(url_for("index"))


@app.route("/users")
def users():
    if "username" in session:
        query = f"""
        SELECT id, username, picture
        FROM users
        WHERE id!={session['user_id']}
        """
    
        with engine.connect() as connection:
            users = connection.execute(query)
    
            return render_template("users.html", users=users)
    else:
        return render_template("404.html"), 404


@app.route("/users/<user_id>")
def user_detail(user_id):
    query = f"""
    SELECT id, username, picture
    FROM users
    WHERE id={user_id}
    """

    with engine.connect() as connection:
        user = connection.execute(query).fetchone()


        if user:
            return render_template("user_detail.html", user=user)
        else:
            return render_template("404.html"), 404

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def handle_login():
    username=request.form["username"]
    password=request.form["password"]

    login_query = f"""
    SELECT password, id
    FROM users
    WHERE username='{username}'
    """

    with engine.connect() as connection:
        user = connection.execute(login_query).fetchone()

        if user and check_password_hash(user[0], password):
            session["user_id"] = user[1]
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("404.html"), 404

@app.route("/logout")
def logout():
    session.pop("username")
    session.pop("user_id")

    return redirect(url_for("index"))




@app.route("/msg_processor/<to_id>", methods=["GET", "POST"])
def msg_processor(to_id):
        text = request.form["text"]
        text = text.replace("'", "''")        
        from_id = session["user_id"]
        to_id = to_id
        
        to_id_query = f"""
        SELECT id
        FROM users
        WHERE username='{to_id}'
        """
        with engine.connect() as connection:
            connection.execute(to_id_query).fetchone()
    
        insert_query = f"""
        INSERT INTO messages(text, from_id, to_id)
        VALUES ('{text}', '{from_id}', {to_id})
        """
        
        with engine.connect() as connection:          
            connection.execute(insert_query)
            
            return redirect(url_for("dm", to_id=to_id))

@app.route("/dm/<to_id>")
def dm(to_id):
    
    messages = []
    if "username" in session:
        
        to_id = to_id        
        
        query = f"""
        SELECT u.id, u.picture, u.username, m.to_id, m.from_id, m.text, m.id
        FROM messages m
        INNER JOIN users u ON m.from_id={session["user_id"]} OR m.from_id={to_id}
        WHERE (m.from_id=u.id)
        AND (m.from_id={to_id} OR m.to_id={to_id})
        AND (m.from_id={session["user_id"]} OR m.to_id={session["user_id"]})
        ORDER BY m.id desc
        """
        
        recipient_query = f"""
        SELECT id, username, picture
        FROM users
        WHERE id={to_id}
        """
        
        with engine.connect() as connection:
            recipient_name = connection.execute(recipient_query).fetchone()
            messages = connection.execute(query).fetchall()
    
    print(messages)
    return render_template("dm.html", messages=messages, recipient_name=recipient_name, to_id=to_id)

@app.route('/dm')
def open_dm():
    if "username" in session:
        query = f"""
        SELECT u.id, u.username, u.picture, m.to_id, m.from_id
        FROM users u
        INNER JOIN messages m ON u.id=to_id OR u.id=from_id
        WHERE (u.id!={session["user_id"]})
    	AND (to_id={session["user_id"]} OR from_id={session["user_id"]})
    	GROUP BY u.id
        """
    
        with engine.connect() as connection:
            users = connection.execute(query)
    
            return render_template("open_dm.html", users=users)
    else:
        return render_template("404.html"), 404




if __name__ == "__main__":
   #app.run(debug=True, port=5000) # comment this line before deploying ONLINE
   app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))