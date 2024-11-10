from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from urllib.parse import quote_plus
import os
import dotenv
from bson import ObjectId
import ast


app = Flask(__name__)

dotenv.load_dotenv()
username = quote_plus(os.getenv("DB_USERNAME"))
password = quote_plus(os.getenv("DB_PASSWORD"))
client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.qovpu.mongodb.net/")
db = client['library_management']

# Check user status
@app.route('/check_user_status', methods=['GET'])
def check_user_status():
    user_id = request.args.get('user_id')
    user = db.users.find_one({'user_id': user_id})
    if user and user['status'] == 'active':
        return jsonify({'status': 'valid'})
    return jsonify({'status': 'invalid'})

# Search books by partial title
# Search books by partial title and return unique titles
@app.route('/search_books', methods=['GET'])
def search_books():
    partial_title = request.args.get('partial_title')
    # Search for books whose title contains the partial title
    books = db.books.find({'book_title': {'$regex': partial_title, '$options': 'i'}}, {'book_title': 1})
    
    # Use a set comprehension to collect unique titles
    unique_titles = list({book['book_title'] for book in books})
    
    return jsonify(unique_titles)


# Get book details by title
@app.route('/get_book_details', methods=['GET'])
def get_book_details():
    book_title = request.args.get('book_title')
    book = db.books.find_one({'book_title': book_title}, {'_id': 0})
    if book:
        if isinstance(book.get('genres'), str):
            book['genres'] = ast.literal_eval(book['genres'])
        if isinstance(book.get('num_pages'), str):
            book['num_pages'] = int(book['num_pages'][0]) if book['num_pages'][0].isdigit() else book['num_pages']
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404

# Create transaction and update inventory by title
@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json
    borrow_date = datetime.strptime(data['borrow_date'], '%Y-%m-%d')
    due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
    book_title = data['book_title']
    
    # Retrieve the book and check availability
    book = db.books.find_one({'book_title': book_title})
    if book and book['available_copies'] > 0:
        transaction = {
            'user_id': data['user_id'],
            'book_title': book_title,
            'borrow_date': borrow_date,
            'due_date': due_date
        }
        
        # Insert the transaction into a borrow_transactions collection
        db.borrow_transactions.insert_one(transaction)
        # Decrease the available copies of the book by 1
        db.books.update_one({'book_title': book_title}, {'$inc': {'available_copies': -1}})
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'unavailable'})

# Notify book unavailability
@app.route('/notify_book_unavailable', methods=['GET'])
def notify_book_unavailable():
    return jsonify({'message': 'Book unavailable notification sent'})

# Notify overdue books
@app.route('/notify_overdue_books', methods=['GET'])
def notify_overdue_books():
    return jsonify({'message': 'Overdue book notification sent'})

if __name__ == '__main__':
    app.run(debug=True)
