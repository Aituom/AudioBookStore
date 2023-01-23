

from flask import Flask, redirect, render_template, request, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout
from sqlalchemy.sql import func
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash


db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rxctfvygbuhnjm cdfgvhbj'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///C:/Users/ACER/PycharmProjects/finalProject/instance/final.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view='/'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Product(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String)
    author=db.Column(db.String)
    speaker=db.Column(db.String)
    price=db.Column(db.String)
    orders=db.relationship('Orders')

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String, unique=True )
    username=db.Column(db.String)
    password=db.Column(db.String)
    is_admin=db.Column(db.Boolean, default=False)
    orders=db.relationship('Orders')

class Orders(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id=db.Column(db.Integer, db.ForeignKey('product.id'))
    date=db.Column(db.DateTime(timezone=True), default=func.now())
def __repr__(self):
        return self.name

@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        email=request.form.get('email')
        username=request.form.get('username')
        password=request.form.get('password')

        user=User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) <4:
            flash('Email must be greater than 4 characters', category='error')

        elif len(username) < 2:
            flash('Username must be greater than 2 characters', category='error')
        elif len(password) < 7:
            flash('Password must be greater than 7 characters', category='error')
        else:
            new_user=User(email=email,username=username,password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            #login_user(user, remember=True)
            return redirect('/')

    return render_template('sign_up.html',user=current_user)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user,remember=True)
                return redirect('/')
            else:
                flash('Incorrect password!', category='error')
        else:
            flash('Email does not exist!', category='error')

    return render_template('login.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/')
def index():

    products = Product.query.order_by(Product.price).all()
    return render_template('index.html', data=products, user=current_user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/buy/<int:id>')
@login_required
def buy(id):
    product = Product.query.get(id)
    order=Orders(user_id=current_user.id, product_id=product.id)
    db.session.add(order)
    db.session.commit()

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "KZT",
        "amount": str(product.price)+'00'
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)

@app.route('/deleteProduct', methods = ['GET','POST'])
def delete():
    if request.method == "POST":
        id = request.form['id']
        try:
            Product.query.filter_by(id=id).delete()
            db.session.commit()
            return redirect('/')
        except:
            return 'error'
    else:
        return render_template('deleteProduct.html')


@app.route('/addProduct', methods = ['GET', 'POST'])
def adding():
    if request.method=="POST":
        name = request.form['name']
        author=request.form['author']
        speaker=request.form['speaker']
        price=request.form['price']
        p = Product(name=name,
                    author=author,
                    speaker=speaker,
                    price=price
             )
        try:
            db.session.add(p)
            db.session.commit()
            return redirect('/')
        except:
            return 'error'

    else:
        return render_template('addProduct.html')

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)