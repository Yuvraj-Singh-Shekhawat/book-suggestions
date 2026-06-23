from flask import Flask, render_template, request
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)


# ---------------- HOME PAGE ----------------
@app.route('/')
def index():

    # ✅ FIX RATING (CLAMP TO 5)
    ratings = popular_df['avg_rating'].values
    ratings = [round(min(r, 5), 2) for r in ratings]

    # ✅ FIX IMAGE QUALITY (M → L)
    images = popular_df['Image-URL-M'].values
    images = [img.replace('-M.jpg', '-L.jpg') for img in images]

    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=images,
        votes=list(popular_df['num_ratings'].values),
        rating=ratings
    )


# ---------------- RECOMMEND UI ----------------
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


# ---------------- RECOMMEND LOGIC ----------------
@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    if not user_input:
        return render_template(
            'recommend.html',
            error="Please enter a book name"
        )

    user_input = user_input.strip().lower()
    pt_index_lower = pt.index.str.lower()

    if user_input not in pt_index_lower.values:
        return render_template(
            'recommend.html',
            error="Book not found. Please enter full book name."
        )

    index = np.where(pt_index_lower == user_input)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]

        title = temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0]
        author = temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0]

        # ✅ HIGH RES IMAGE
        image = temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0]
        image = image.replace('-M.jpg', '-L.jpg')

        data.append([title, author, image])

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
