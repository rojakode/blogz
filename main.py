from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils_hash_n_salt import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lovesu@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.route("/login", methods=['POST','GET'])
def login():

    if request.method == 'POST':
        username = request.form['username_f']
        password = request.form['password_f']
        user = User.query.filter_by(username=username).first()

        if user == None:
            flash('Username does not exist', 'user')
            return render_template('login.html')
        elif not check_pw_hash(password, user.pw_hash):
            flash('User password incorrect', 'pwd')
            return render_template('login.html')
        else:
            session['username'] = username
            return redirect('/blog?user='+str(user.id))
    
    return render_template('login.html')

@app.route("/signup", methods = ['POST','GET'])
def signup():

    if request.method == "POST":
        username = request.form['username_f']
        pwd = request.form['password_f']
        verify = request.form['verify_f']

        username_error = ''
        password1_error = ''
        password2_error = ''
        error_check = False

        user = User.query.filter_by(username=username).first()
        if user != None:
            print(user.username)

        if user != None:
            if user.username == username:
                username_error = 'Username already exists'
                error_check = True

        elif username == '':
            username_error = 'Thats not a valid Username'
            error_check = True

        elif ' ' in username:
            username_error = 'Username cannot contain a space'
            error_check = True

        elif len(username) < 3 or len(username) > 20:
            username_error = 'Username must be between 3 and 20 characters long'
            error_check = True

        if pwd == '':
            password1_error = 'Thats not a valid Password'
            error_check = True

        elif ' ' in pwd:
            password1_error = 'Password cannot contain a space'
            error_check = True

        elif len(pwd) < 3 or len(pwd) > 20:
            password1_error = 'Password must be between 3 and 20 characters long'
            error_check = True

        if not (pwd == verify):
            password1_error = 'Passwords dont match'
            password2_error = 'Passwords dont match'
            error_check = True

        if error_check == True:
            return render_template('signup.html', username_error = username_error, password1_error = password1_error, password2_error = password2_error)
        else:
            new_user = User(username, pwd)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')    

@app.route("/logout")
def logout():
    print(session)
    if session:
        del session['username']
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['index','login', 'list_blogs', 'signup', 'logout']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/newpost", methods = ['POST','GET'])
def newpost():
    if request.method == "POST":
        title = request.form['title_f']
        body = request.form['body_f']
    
        if request.form['title_f'] == '':
            errorT = 'Please fill in the title'
        else:
            errorT = ''
        
        if request.form['body_f'] == '':
            errorB = 'Please fill in the body'
        else:
            errorB = ''
            
        if errorB or errorT:
            return render_template('newpost.html',errorTitle=errorT,errorBody=errorB,title_p=title,body_p=body)
        else:
            entry_title = request.form['title_f']
            entry_body = request.form['body_f']

            user = session['username']
            user_id = User.query.filter_by(username=user).first()
            blog_entry = Blog(entry_title, entry_body, user_id)
            db.session.add(blog_entry)
            db.session.commit()

            value_id = blog_entry.id
            return redirect('/blog?id='+str(value_id))

    return render_template('newpost.html')

@app.route("/blog", methods=['GET'])
def list_blogs():
    value_id = request.args.get('id')
    value_user = request.args.get('user')

    if value_user:
        user_blogs = Blog.query.filter_by(owner_id=value_user).all()
        return render_template('blogpost.html',user=user_blogs,value_u=value_user)
    elif value_id:
        blog_x = Blog.query.filter_by(id=value_id).all()
        return render_template('blogpost.html',blog=blog_x,value_i=value_id)
    else:
        blogs = Blog.query.all()
        return render_template('blogpost.html',blogs=blogs)

@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()