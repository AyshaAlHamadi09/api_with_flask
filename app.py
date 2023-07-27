from flask import Flask, jsonify, request
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from book_storage import BOOKS


app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def valid_book_data(data):
    if 'author' not in data or 'title' not in data:
        return False
    return True



@app.route('/api/books', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def books():
    if request.method == 'GET':
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        author = request.args.get('author')

        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_books = BOOKS[start_index:end_index]

        if author:
            filtered_books = [book for book in BOOKS if book['author'] == author]
            return jsonify(filtered_books)
        return jsonify(paginated_books)

    elif request.method == 'POST':
        new_book = request.get_json()
        if not valid_book_data(new_book):
            return jsonify({"error": "Invalid book data"}), 400
        new_id = max(book['id'] for book in BOOKS) + 1
        new_book['id'] = new_id
        BOOKS.append(new_book)
        return jsonify(new_book), 201


def find_book_by_id(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            return book
    return None


@app.route('/api/books/<int:id>', methods=['PUT'])
def handle_book(id):
    book = find_book_by_id(id)
    if book is None:
        return '', 404
    new_data = request.get_json()
    book.update(new_data)
    return jsonify(book)


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete(id):
    book = find_book_by_id(id)
    if book is None:
        return '', 404
    BOOKS.remove(book)
    return jsonify(book)


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)