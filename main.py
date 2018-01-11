from flask import Flask, request, redirect, render_template, session, flash, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:aaaaaa@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'Lwa7V0I42c5WIFpC'

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(40))
    Post = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/logout')
def logout():
    del session['username']
    flash ('Logged Out!')
    return redirect('/blog')

@app.route('/login', methods=['Post','GET'])
def login():
    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = "Invalid username or password"
        user = User.query.filter_by(username=username).first()

        if user:
            
            if user.password == password:
            
                session['username'] = username
                flash('Logged in!')
                return redirect('/AddPost')
            else: 

                flash ('Invalid Password', 'error')    

    
        else:
            
            flash('Invalid Username', 'error')

    
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
 
        error2 = ""
        error3 = ""
        error4 = ""
    
        

            
        existing_user = User.query.filter_by(username=username).first()
        
        if len(username) < 3:
            error2 = "Invalid username"
            
        if len(password) < 3:
            error3 = "Invalid password"
            
        if password != verify or len(verify) < 1:
            error4 = "Passwords do not match"  

        if error2 or error3 or error4: 

            return render_template('register.html', username = username, error2 = error2, error3 = error3, error4 = error4)   
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username

            return redirect('/AddPost')

        else:
            flash ('User already exist')
            return render_template('register.html', username = username)
    
    return render_template('register.html')



@app.route('/blog', methods=['POST','GET'])
def blog():
    
    post_id = request.args.get('id')

    post_user = request.args.get('user')
    print (post_user)
    user_filt = User.query.filter_by(username=post_user).first()
    if post_id:
        indv_post = Post.query.get(post_id)
        return render_template('indv_post.html', indv_post=indv_post)
    if user_filt:
        
        
        user_posts = Post.query.filter_by(owner_id=user_filt.id).all()
        return render_template('userspost.html', user_posts=user_posts)
    else:
        post = Post.query.all()

        return render_template('blog.html', post=post)



@app.route('/AddPost', methods=['POST','GET'])
def add_post():
    
    error = ""
    error2 = ""
    owner = User.query.filter_by(username=session['username']).first()
     
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        
        
        if len(post_title) < 1:
            error = "field is empty"

        if len(post_body) < 1:
            error2 = "field is empty"
        
        if error or error2:
        
            return render_template('AddPost.html', title="Build-A-Blog", error = error, error2 = error2, post_title = post_title, post_body = post_body) 

        new_post = Post(post_title,post_body,owner.id)
        db.session.add(new_post)
        db.session.commit() 


        return redirect('/blog?id=%s' % new_post.id)

        
    return render_template('AddPost.html', title="Build-A-Blog")


@app.route('/', methods=['POST', 'GET'])
def index():
   
    users = User.query.all()
    return render_template('Home.html',title="Build-A-Blog", 
        users = users)


if __name__ == '__main__':
    app.run()