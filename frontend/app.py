import streamlit as st
import requests
from datetime import datetime, timedelta

# Set up base URL for the Flask API
BASE_URL = "http://localhost:5000"

st.title("Library System")

# Search bar for books
st.subheader("Search for a Book")
partial_title = st.text_input("Start typing the book title...")

# Fetch search results based on partial title
if partial_title:
    search_response = requests.get(f"{BASE_URL}/search_books", params={"partial_title": partial_title})
    if search_response.status_code == 200:
        search_results = search_response.json()
        selected_book_title = st.selectbox("Select a book from the list:", search_results)
    else:
        st.error("Could not fetch book titles.")
else:
    selected_book_title = None

# Display book details if a title is selected
if selected_book_title:
    details_response = requests.get(f"{BASE_URL}/get_book_details", params={"book_title": selected_book_title})
    
    if details_response.status_code == 200:
        book_details = details_response.json()
        
        # Display book information
        st.image(book_details['cover_image_uri'], width=200)
        st.write(f"**Title:** {book_details['book_title']}")
        st.write(f"**Author:** {book_details['author']}")
        st.write(f"**Genres:** {', '.join(book_details['genres'])}")
        st.write(f"**Details:** {book_details['book_details']}")
        st.write(f"**Available Copies:** {book_details['available_copies']}")
        
        # Borrow book functionality
        borrow = st.button("Borrow this Book")
        
        if borrow:
            user_id = "user1"  # This could be dynamic in a real-world scenario
            borrow_date = datetime.today().strftime('%Y-%m-%d')
            due_date = (datetime.today() + timedelta(days=14)).strftime('%Y-%m-%d')
            
            borrow_response = requests.post(
                f"{BASE_URL}/create_transaction",
                json={
                    "user_id": user_id,
                    "book_title": selected_book_title,
                    "borrow_date": borrow_date,
                    "due_date": due_date
                }
            )
            
            if borrow_response.status_code == 200:
                result = borrow_response.json()
                if result['status'] == 'success':
                    st.success("Book borrowed successfully!")
                else:
                    st.warning("The book is currently unavailable.")
            else:
                st.error("Failed to borrow the book.")
    else:
        st.error("Could not fetch book details.")
