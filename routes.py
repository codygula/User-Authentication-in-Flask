from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    request
)

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
import json
import scratchpad
import boto3

from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app,db,login_manager,bcrypt
from models import User
from forms import login_form,register_form

dbclient = boto3.resource("dynamodb")
searchdatabase = dbclient.Table("searchItems")
AuthTable = dbclient.Table("email_list")



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    resp = scratchpad.query_table('searchItems', 'email', '222222')
    posts = resp.get('Items')
    return render_template("index.html",title="Home", posts=posts)


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    print("login called")
    form = login_form()

    if form.validate_on_submit():
        print('form.validate_on_submit() called')
        try:
            print('try thing entered')
            user = form.email.data
            password = form.pwd.data
            print(user)
            response = AuthTable.get_item(
                TableName="email_list",
                Key={
                    "email": user
                })
            
            
            dbpassword = response['Item']['passwordhash']
            print('dbpassword = ', dbpassword)
            print('password = ', password)


            if check_password_hash(dbpassword, password):
                print("logging in!!!!!!!!!!!!")
                resp = scratchpad.query_table('searchItems', 'email', '222222')
                posts = resp.get('Items')
                print("No errors before login_user !!!!!!!!!!!!")
               
                print("No errors after login_user !!!!!!!!!!!!")
                return render_template('dashboard.html', posts=posts, user=user)

            else:
                print("check pasword failed")
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")
            print("except thing happened")
    print('Right before return render_template()')
    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            # put dynamoDB stuff here?
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
            ############################# This works
            pwdhash=bcrypt.generate_password_hash(pwd).decode('utf-8')
            response = AuthTable.put_item(
                Item={
                    "email": email,
                    "password": pwd,
                    "passwordhash": pwdhash,
                    })
            print(response) 


            #############################
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/DeleteItem',  methods =["POST"])
def DeleteItem():
    information = request.data
    deleteThis = int(information.decode("utf-8"))
    # replace with email from login
    email = '222222'
    response = scratchpad.delete_info(email, deleteThis)
    print(response)
   
    resp = scratchpad.query_table('searchItems', 'email', '222222')
    posts = resp.get('Items')
    return render_template('index.html', posts=posts)

@app.route('/TestItem', methods = ["POST"])
def TestItem():
    information = request.data
    # information = request.form
    testThis = int(information.decode("utf-8"))

    # insert code to send a test email
    print('TestItem() called!!!! testThis= ', testThis)

    resp = scratchpad.query_table('searchItems', 'email', '222222')
    posts = resp.get('Items')
    return render_template('index.html', posts=posts)
 

@app.route('/AddItem', methods=["GET","POST"])
def AddItem():
    print("AddItem() Called")

    information = request.data
    testThis = (information.decode("utf-8"))
    data = json.loads(testThis)

    print("testThis= ", testThis)
    print("AddItem() data[item] = ", data["item"])
    print("AddItem() data[URL] = ", data["URL"])

    response = scratchpad.put_info('222222', data["URL"], data["item"])
    print(response)


    resp = scratchpad.query_table('searchItems', 'email', '222222')
    posts = resp.get('Items')
    
    return render_template('index.html', posts=posts)


if __name__ == "__main__":
    app.run(debug=True)
