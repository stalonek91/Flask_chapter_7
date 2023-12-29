from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import date


app = Flask(__name__) #initialize Flask instance

app.config.from_pyfile('config.cfg') #importing config file for our DB

db = SQLAlchemy(app)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(30))
    password = db.Column(db.String(50))
    join_date = db.Column(db.DateTime)

    orders = db.relationship('Order', backref='member', lazy='dynamic')
    courses = db.relationship('Course', secondary='user_courses', backref='member', lazy='dynamic')

    def __repr__(self) -> str:
        return f'Member: {self.username}'
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


db.Table('user_courses',
    db.Column('member_id', db.Integer, db.ForeignKey('member.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

def create_member(username, email, password):
    new_member = Member(username=username, email=email, password=password, join_date=date.today())

    db.session.add(new_member)
    db.session.commit()

    print(f'User {new_member} created')

    return new_member


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = Member.query.filter_by(username=username).first()

        if existing_user:
            print(f'User: {username} found in the database. Updating')
            existing_user.email = email
            existing_user.password = password
        else:
            new_member = Member(username=username, email=email, password=password, join_date=date.today())
            db.session.add(new_member)

        db.session.commit()

        return redirect(url_for('users'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        user_to_delete = request.form.get('delete_username')
        user_from_db_to_delete = Member.query.filter_by(username=user_to_delete).first() 

        if user_from_db_to_delete:
            db.session.delete(user_from_db_to_delete)
            db.session.commit()


    return redirect(url_for('users'))


@app.route('/users')
def users():

    all_users = Member.query.order_by(Member.email).all()
    all_users_number = Member.query.count()
    ### all_users = Member.query.order_by(Member.email).limit(2).all() z limitem
    not_complete_users = Member.query.filter(db.or_(Member.username == 'Kasia', Member.username == 'Sylwek')).order_by(Member.id).all()
    print(not_complete_users)

    return render_template('users.html', users=all_users, not_complete_users=not_complete_users, user_count = all_users_number)

@app.route('/orders')
def orders():

    all_users = Member.query.all()
    all_orders = Order.query.all()
    return render_template('orders.html', users = all_users, orders=all_orders)


    
@app.route('/add_order', methods=['POST'])
def add_order():

    if request.method == 'POST':
        order_user_id = request.form.get('user_id')
        order_price = request.form.get('price')

        # #getting user based on user_id
        # user_object = Member.query.filter(Member.id==order_user_id).first()
        # print(user_object)

        #creating entry in Orders table
        new_order = Order(price=order_price, member_id = order_user_id)
        # #checkin if memory backwards relation works
        # new_order_test = Order(price=1000, member=user_object)
        db.session.add(new_order)
        db.session.commit()

    return redirect(url_for('orders'))

@app.route('/add_course', methods=['POST'])
def add_course():

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        new_course = Course(name=course_name)

        db.session.add(new_course)
        db.session.commit()
    
    return redirect(url_for('courses'))



@app.route('/courses')
def courses():
    
    all_courses = Course.query.all()

    result = db.session.execute(text('SELECT * FROM user_courses'))
    table_data = result.fetchall()

    
    return render_template('courses.html', courses=all_courses, table_mapping = table_data)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run()

    