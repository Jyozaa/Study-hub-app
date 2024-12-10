from flask import json,render_template, redirect, url_for, flash, request, session
from app import app, db, admin
from .forms import AssessmentForm, RegisterForm, LoginForm, EditProfileForm
from .models import Assessment, User, StudySession, Course, CourseMessage
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

from flask_login import LoginManager, login_user, logout_user, current_user, login_required

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Assessment, db.session))
admin.add_view(ModelView(StudySession, db.session))
admin.add_view(ModelView(Course, db.session))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('home.html', user=current_user, users=users)



@app.route('/assessments', methods=['GET', 'POST'])
@login_required
def assessments():
    form = AssessmentForm()
    assessments = Assessment.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        due_date = form.due_date.data
        module_code = form.module_code.data
        title = form.title.data

        if due_date < datetime.now().date():
            flash("Due date cannot be in the past.", "danger")
            return render_template('assessments.html', user=current_user, form=form, assessments=assessments)

        existing_assessment = Assessment.query.filter_by(module_code=module_code, title=title).first()
        if existing_assessment:
            flash("Cannot have duplicate assessments.", "danger")
            return render_template('assessments.html', user=current_user, form=form, assessments=assessments)
        
        new_assessment = Assessment(
            module_code=form.module_code.data,
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            user_id=current_user.id
        )
        db.session.add(new_assessment)
        db.session.commit()
        flash('New assessment added!', 'success')
        return redirect(url_for('assessments'))

    return render_template('assessments.html', user=current_user, form=form, assessments=assessments)




@app.route('/assessments/<int:id>/edit', methods=['GET', 'POST'])
def edit_assessment(id):
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('assessments'))
   
    form = AssessmentForm(obj=assessment)

    if form.validate_on_submit():
        module_code = form.module_code.data
        title = form.title.data

        duplicate = Assessment.query.filter(
            Assessment.module_code == module_code,
            Assessment.title == title,
            Assessment.id != id,  
            Assessment.user_id == current_user.id
        ).first()

        if duplicate:
            flash("An assessment with the same module code and title already exists.", "danger")
            return render_template('edit_assessment.html', form=form, assessment=assessment)


        assessment.module_code = form.module_code.data
        assessment.title = form.title.data
        assessment.description = form.description.data
        assessment.due_date = form.due_date.data
        db.session.commit()
        flash('Assessment updated successfully!', 'success')
        return redirect(url_for('assessments'))

    return render_template('edit_assessment.html', form=form, assessment=assessment)



@app.route('/assessments/<int:id>/complete')
@login_required
def complete_assessment(id):

    if not Assessment.query.first():  
        flash('No data available. Redirecting to home page.', 'warning')
        return redirect(url_for('home'))
    
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('assessments'))
    
    if not assessment.completed:  
        assessment.completed = True
        current_user.add_exp(20) 
        db.session.add(current_user)  
        db.session.commit()

        flash(f'Task completed! You earned 20 XP. Congratulations! Your current level is {current_user.level} with {current_user.exp}/{current_user.level * 100} XP.', 'success')
    else:
        flash('Task was already marked as complete.', 'info')
    db.session.commit()
    return redirect(url_for('assessments'))



@app.route('/assessments/<int:id>/uncomplete')
@login_required
def uncomplete_assessment(id):

    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('assessments'))
    
    assessment.completed = False
    current_user.add_exp(-20)  
    db.session.add(current_user)  
    db.session.commit()
    flash(f'Task un-completed 20 EXP has been deducted. Your current level is {current_user.level} with {current_user.exp}/{current_user.level * 100} EXP.', 'danger')
    return redirect(url_for('assessments'))



@app.route('/assessments/<int:id>/delete')
@login_required
def delete_assessment(id):
    
    assessment = Assessment.query.get_or_404(id)
    if assessment.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('assessments'))
    
    db.session.delete(assessment)
    db.session.commit()
    flash('Assessment deleted.', 'danger')
    return redirect(url_for('assessments'))



@app.route('/leaderboard')
def leaderboard():
    if not User.query.first(): 
        flash('Register/Login to access this page', 'warning')
        return redirect(url_for('home'))
    
    users = User.query.order_by(User.level.desc(), User.exp.desc()).all()
    return render_template('leaderboard.html', user=current_user, users=users)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/my_profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    form = EditProfileForm(obj=user)

    if form.validate_on_submit():

        if not user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('edit_profile.html', form=form, user=user)

        if form.username.data != user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('This username is already taken.', 'danger')
                return render_template('edit_profile.html', form=form, user=user)
            user.username = form.username.data

    
        if form.email.data != user.email:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('This email is already registered.', 'danger')
                return render_template('edit_profile.html', form=form, user=user)
            user.email = form.email.data

       
        if form.new_password.data:
            user.set_password(form.new_password.data)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('my_profile'))

    return render_template('edit_profile.html', form=form, user=user)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session.clear()
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))



@app.route('/study', methods=['GET','POST'])
@login_required
def study():

    study_sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.start_time.desc()).all() or []
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()

    return render_template('study.html', user=current_user.id, study_sessions=study_sessions, active_session=active_session)



@app.route('/study/start', methods=['POST'])
@login_required
def start_study():

    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    if active_session:
        flash('You already have an active study session', 'warning')
    
    new_session = StudySession(user_id=current_user.id, start_time=datetime.now())
    db.session.add(new_session)
    db.session.commit()
    flash('Study session started!', 'success')

    return redirect(url_for('study'))



@app.route('/study/stop', methods=['POST'])
@login_required
def stop_study():
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    if not active_session:
        flash('No active study session found.', 'danger')
        return redirect(url_for('study'))
    
    active_session.end_time = datetime.now()
    active_session.duration = (active_session.end_time - active_session.start_time).seconds

    current_user.total_study_time += active_session.duration

    exp_gained = (active_session.duration // 30)*10

    session_minutes = active_session.duration // 60
    session_seconds = active_session.duration % 60
    current_user.add_exp(exp_gained)
    db.session.commit()
    flash(f'Study session stopped! Duration: {session_minutes} minutes {session_seconds} seconds. You earned {exp_gained} exp.', 'success')
    return redirect(url_for('study'))



@app.route('/user/<int:id>')
@login_required
def view_profile(id):
    user = User.query.get_or_404(id)
    study_sessions = StudySession.query.filter_by(user_id=id).order_by(StudySession.start_time.desc()).all()
    badge = user.getbadge()
    enrolled_courses = user.courses
    return render_template('profile.html', user=user, study_sessions=study_sessions, badge=badge,  courses=enrolled_courses)


@app.route('/search_users')
@login_required
def search_users():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return json.dumps({"users": []})

    matching_users = User.query.filter(User.username.ilike(f"%{query}%"), User.id != current_user.id).all()
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "level": user.level,
            "total_study_time": user.total_study_time,
        }
        for user in matching_users
    ]
    return json.dumps({"users": users_data}), {"Content-Type": "application/json"}



@app.route('/my_profile/followers')
@login_required
def followers():
    followers = current_user.followers if current_user.followers else []
    return render_template('followers.html', user=current_user, followers=followers)



@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    
    other_user = User.query.get(user_id)

    if other_user not in current_user.followed:
        current_user.followed.append(other_user)
        db.session.commit()
        flash(f"You are now following {other_user.username}!", "success")
    else:
        flash("You are already following this user.", "info")

    return redirect(url_for('home'))


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    other_user = User.query.get(user_id)

    if other_user in current_user.followed:
        current_user.followed.remove(other_user)
        db.session.commit()
        flash(f"You unfollowed {other_user.username}.", "success")
    else:
        flash("You are not following this user.", "info")

    return redirect(url_for('home'))


@app.route('/following')
@login_required
def following():
    following_users = current_user.followed.all()
    return render_template('following.html', user=current_user, following=following_users)



@app.route('/my_profile')
@login_required
def my_profile():
    study_sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.start_time.desc()).all()
    badge = current_user.getbadge() 
    enrolled_courses = current_user.courses  

    return render_template('my_profile.html', user=current_user, study_sessions=study_sessions, badge=badge, courses=enrolled_courses)



@app.route('/courses')
@login_required
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', user=current_user, courses=all_courses)



@app.route('/courses/<int:course_id>/enrolled_users', methods=['GET', 'POST'])
def enrolled_users(course_id):  
    course = Course.query.get_or_404(course_id)
    enrolled_users = course.users 
    
    if request.method == 'POST' and current_user in enrolled_users:
        message_content = request.form.get('message')
        if message_content:
            new_message = CourseMessage(content=message_content, user=current_user, course=course)
            db.session.add(new_message)
            db.session.commit()
            flash('Message sent.', 'success')
        else:
            flash('Message cannot be empty.', 'danger')

    
    messages = CourseMessage.query.filter_by(course_id=course.id).order_by(CourseMessage.time.desc()).all()

    return render_template('enrolled_users.html', course=course, users=enrolled_users, user=current_user, messages=messages)



@app.route('/courses/enroll/<int:course_id>')
@login_required
def enroll_in_course(course_id):
    course = Course.query.get(course_id)
    if course not in current_user.courses:
        current_user.courses.append(course)
        db.session.commit()
        flash(f"successfully enrolled in {course.title}!", "success")
    else:
        flash("You are already enrolled in this course.", "info")

    return redirect(url_for('courses'))


@app.route('/courses/unenroll/<int:course_id>')
@login_required
def unenroll_from_course(course_id):
    course = Course.query.get(course_id)

    if course in current_user.courses:
        current_user.courses.remove(course)
        db.session.commit()
        flash(f"You have been unenrolled from {course.title}.", "success")
    else:
        flash("You are not enrolled in this course.", "info")

    return redirect(url_for('courses'))

