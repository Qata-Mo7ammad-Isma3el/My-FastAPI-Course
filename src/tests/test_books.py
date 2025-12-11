
books_prefix = "/api/v1/books"

def test_get_all_books(test_client, fake_book_service, fake_db_session):
    """Test getting all books endpoint."""
    fake_books = [
        {"id": 1, "title": "Book One", "author": "Author A"},
        {"id": 2, "title": "Book Two", "author": "Author B"},
    ]
    fake_book_service.get_all_books.return_value = fake_books

    response = test_client.get(url=books_prefix)
    assert fake_book_service.get_all_books_called_once_with(fake_db_session)