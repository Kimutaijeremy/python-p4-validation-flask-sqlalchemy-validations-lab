from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Author, Post
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

# Custom validation functions
def validate_author(data):
    errors = {}
    
    # Name validation
    if not data.get('name'):
        errors['name'] = ['Name is required']
    
    # Phone number validation
    phone = data.get('phone_number')
    if phone and (len(phone) != 10 or not phone.isdigit()):
        errors['phone_number'] = ['Phone number must be exactly 10 digits']
    
    return errors

def validate_post(data):
    errors = {}
    
    # Title validation for clickbait
    title = data.get('title')
    if title:
        clickbait_keywords = ["Won't Believe", "Secret", "Top", "Guess"]
        if not any(keyword in title for keyword in clickbait_keywords):
            errors['title'] = ['Title must contain one of: "Won\'t Believe", "Secret", "Top", "Guess"']
    
    # Content validation
    content = data.get('content')
    if content and len(content) < 250:
        errors['content'] = ['Content must be at least 250 characters long']
    
    # Summary validation
    summary = data.get('summary')
    if summary and len(summary) > 250:
        errors['summary'] = ['Summary must be a maximum of 250 characters']
    
    # Category validation
    category = data.get('category')
    valid_categories = ['Fiction', 'Non-Fiction']
    if category and category not in valid_categories:
        errors['category'] = ['Category must be either Fiction or Non-Fiction']
    
    return errors

@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    errors = validate_author(data)
    
    if errors:
        return jsonify({'errors': errors}), 422
    
    # Check for duplicate name
    existing_author = Author.query.filter_by(name=data['name']).first()
    if existing_author:
        return jsonify({'errors': {'name': ['Name must be unique']}}), 422
    
    author = Author(
        name=data['name'],
        phone_number=data.get('phone_number')
    )
    
    db.session.add(author)
    db.session.commit()
    
    return jsonify({
        'id': author.id,
        'name': author.name,
        'phone_number': author.phone_number
    }), 201

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    errors = validate_post(data)
    
    if errors:
        return jsonify({'errors': errors}), 422
    
    post = Post(
        title=data['title'],
        content=data.get('content'),
        category=data.get('category'),
        summary=data.get('summary'),
        author_id=data.get('author_id')
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'category': post.category,
        'summary': post.summary
    }), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)