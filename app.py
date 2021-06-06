from flask import Flask, flash, redirect, render_template, request, session
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, Users, Feedback
from forms import UserForm, FeedbackForm, LoginForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'crowBottom'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home():
    return render_template('home.html')

# USER ROUTES ##################################################################

@app.route('/register', methods=['GET', 'POST'])
# register a new user
def register_user():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        new_user = Users.register(username, password, first_name, last_name, email)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash(f'Welcome {username}! Successfully Created Your Account!')
        return redirect('/feedback')
    return render_template('/register.html', form=form)

@app.route('/login', methods=['GET','POST'])
# login
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = Users.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            return redirect(f'/users/{user.id}')
        else:
            form.username.errors = ['Invalid username/password.']
    return render_template('login.html', form=form)

@app.route('/logout')
# Logout
def logout_user():
    session.pop('user_id')
    flash("Goodbye!")
    return redirect('/')

@app.route('/users/<int:user_id>')
def user_page(user_id):
    user = Users.query.get_or_404(user_id)
    feedback = Feedback.query.all()
    return render_template('user_details.html', user=user, feedback=feedback)

# FEEDBACK ROUTES ##############################################################

@app.route('/feedback', methods=['GET', 'POST'])
def show_feedback():
    if "user_id" not in session:
        flash("Please login first", 'w3-flame')
        return redirect('/')
    form = FeedbackForm()
    all_feedback = Feedback.query.all()
    if form.validate_on_submit():
        text = form.text.data
        new_feedback = Feedback(text=text, user_id=session["user_id"])
        db.session.add(new_feedback)
        db.session.commit()
        flash("Thank You For the Feedback!")
        return redirect('/feedback')

    return render_template('feedback.html', form=form, all_feedback=all_feedback)

@app.route('/feedback/<int:id>', methods=["POST"])
def delete_feedback(id):
    if 'user_id' not in session:
        flash("Please login first")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(id)
    if feedback.user_id == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedabck deleted")
        return redirect('/feedback')
    flash("You don't have permission")
    return redirect('/feedback')
