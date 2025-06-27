from flask import Flask, render_template, url_for, redirect
from flask.cli import load_dotenv
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import DeclarativeBase
from wtforms.fields.simple import SubmitField
from bs4 import BeautifulSoup
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)


class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)


class TodoForm(FlaskForm):
    todo_content = CKEditorField("Write you to-do list")
    submit = SubmitField("Submit")

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/post', methods=["GET","POST"])
def create_post():
    form = TodoForm()
    if form.validate_on_submit():
        raw_html = form.todo_content.data
        text = BeautifulSoup(raw_html, "html.parser").get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            new_todo = Todo(content=line)
            db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for("create_post"))

    todos = Todo.query.all()
    return render_template("post.html", form=form, todos=todos)

@app.route('/aboutus')
def about_us():
    return render_template("background.html")

@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    todo_to_delete = db.get_or_404(Todo, todo_id)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('create_post'))



if __name__ == "__main__":
    app.run(debug=True, port=5002)