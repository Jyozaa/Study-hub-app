from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin


user_courses = Table(
    "user_courses",
    db.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("course_id", Integer, ForeignKey("course.id"))
)

follows = Table(
    "follows",
    db.metadata,
    Column("follower_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("followed_id", Integer, ForeignKey("user.id"), primary_key=True)
)

class Course(db.Model):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True)
    title = Column(db.String(150), nullable=False)
    description = Column(db.Text, nullable=True)
    users = relationship("User", secondary=user_courses, backref="courses")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    level = db.Column(db.Integer, default=1)
    exp = db.Column(db.Integer, default=0)
    total_study_time = db.Column(db.Integer, default=0)
    followed = relationship(
        "User", secondary=follows,
        primaryjoin=(follows.c.follower_id == id),
        secondaryjoin=(follows.c.followed_id == id),
        backref="followers",
    )


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_exp(self, amount):
        if amount > 0:
            self.exp += amount
            while self.exp >= self.level * 100:
                self.exp -= self.level * 100
                self.level += 1

        elif amount < 0:
            self.exp += amount
            while self.exp < 0 and self.level > 1:
                self.level -= 1
                self.exp += self.level * 100
            
            if self.level == 1 and self.exp < 0:
                self.exp = 0
    
    def getbadge(self):
        session_count = StudySession.query.filter_by(user_id=self.id).count()
        
        if session_count >= 70:
            return 'nether.png'
        elif session_count >= 60:
            return 'diamond.png'
        elif session_count >= 50:
            return 'gold_badge.png'
        elif session_count >= 40:
            return 'iron.png'
        elif session_count >= 30:
            return 'mutton.png'
        elif session_count >= 20:
            return 'salmon.png'
        elif session_count >= 10:
            return 'rotten.png'
        else:
            return 'nobadge' 



class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer, default=0)



class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_code = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)




class CourseMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now())

    user = db.relationship("User", backref="messages")
    course = db.relationship("Course", backref="messages")
