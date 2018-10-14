from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:surekha@123@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False

@app.route("/")
def index():
    entries = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('base.html',entries=entries)

@app.route("/newpost", methods = ['POST','GET'])
def newpost():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        title_err = ""
        body_err = ""
    
        if title == "":
            title_err = "Please add a title to your Post."

        if body == "":
            body_err = "Please write a post for your blog here."
        
        if title_err != "" or body_err != "":
            return render_template('newpost.html',title=title,body=body,title_err=title_err,body_err=body_err)
        else:
            new_entry = Blog(title,body)
            db.session.add(new_entry)
            db.session.commit()
            newentry = Blog.query.order_by(Blog.id.desc()).first()
            id = newentry.id
            return redirect("/blogpost?id={}".format(id))

    return render_template('newpost.html')

@app.route("/blogpost", methods=['GET'])
def blogpost():
    id = request.args.get('id')
    entry = Blog.query.filter_by(id=id).first()
    title = entry.title
    body = entry.body

    return render_template('blogpost.html',title=title,body=body)

if __name__ == '__main__':
    app.run()