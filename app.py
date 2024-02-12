from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required
from werkzeug.security import check_password_hash
from models import db, Event, Attendee, User
from question_analysis import filter_questions

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

with app.app_context():
    db.create_all()

mail = Mail(app)

login_manager = LoginManager(app)  # Initialize LoginManager with the Flask app
login_manager.login_view = 'login'  # Specifying the route where login is handled

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':

        event_date_str = request.form['event_date']
        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()

        interactive_links = ','.join(request.form.getlist('interactive_links'))

        event = Event(
            name=request.form['name'],
            zoom_link=request.form['zoom_link'],
            interactive_links=interactive_links,
            event_date=event_date,
            other_details=request.form['other_details']
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('list_events', event_id=event.id))
    return render_template('create_event.html')

#To view and edit events:
@app.route('/events')
@login_required
def list_events():
    events = Event.query.all()
    return render_template('list_events.html', events=events)

@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.zoom_link = request.form['zoom_link']
        # Handle interactive_links as a single string separated by commas
        event.interactive_links = ','.join(request.form.getlist('interactive_links[]'))
        event.other_details = request.form['other_details']
        db.session.commit()
        return redirect(url_for('list_events'))
    attendees = Attendee.query.filter_by(event_id=event.id).all()
    return render_template('event_details.html', event=event, attendees=attendees, event_id=event_id)

@app.route('/event/<int:event_id>/appropriate_questions')
@login_required
def show_appropriate_questions(event_id):
    event = Event.query.get_or_404(event_id)
    questions = filter_questions(event_id)
    return render_template('appropriate_questions.html', questions=questions, event_name=event.name)

@app.route('/send_message_to_attendees', methods=['GET', 'POST'])
@login_required
def send_message_to_attendees():
    if request.method == 'POST':
        event_id = request.form['event_id']
        message = request.form['message']
        subject = request.form['subject']
        attendees = Attendee.query.filter_by(event_id=event_id).all()
        with mail.connect() as conn:
            for attendee in attendees:
                msg = Message(subject=subject, sender=app.config['MAIL_USERNAME'], recipients=[attendee.email])
                msg.body = message
                conn.send(msg)
        return 'Messages sent successfully!'
    else:
        events = Event.query.all()
        return render_template('send_message.html', events=events)
    
    

#For attendees
@app.route('/registration_events')
def registration_events():
    events = Event.query.all()
    return render_template('registration_events.html', events=events)

@app.route('/event/<int:event_id>/register', methods=['GET', 'POST'])
def register_attendee(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        # Process the registration form submission
        attendee = Attendee(
            name=request.form['name'],
            email=request.form['email'],
            question=request.form['question'],
            event_id=event_id
        )
        db.session.add(attendee)
        db.session.commit()
        return redirect(url_for('registration_success', event_id=event_id))
    return render_template('register_attendee.html', event=event)

@app.route('/event/<int:event_id>/registration_success')
def registration_success(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('registration_success.html', event=event)


if __name__ == '__main__':
    #with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    app.run(debug=True)

