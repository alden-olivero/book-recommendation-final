from flask import Flask,render_template,request
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['title'].values),
                           author=list(popular_df['author'].values),
                           image=list(popular_df['img_url'].values),
                           votes=list(popular_df['num_of_rating'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('title')['title'].values))
        item.extend(list(temp_df.drop_duplicates('title')['author'].values))
        item.extend(list(temp_df.drop_duplicates('title')['img_url'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)


def recommend_book(book_name):
    from scipy.sparse import csr_matrix
    book_sparse=csr_matrix(pt)
    book_sparse
    from sklearn.neighbors import NearestNeighbors
    model=NearestNeighbors(algorithm="brute")
    model.fit(book_sparse)
    try:
        book_id = pt.index.get_loc(book_name)
    except KeyError:
        return []
    distance, suggestion = model.kneighbors(pt.iloc[book_id, :].values.reshape(1, -1), n_neighbors=6)

    recommended_books = []
    for i in range(len(suggestion)):
        books = pt.index[suggestion[i]+1]
        for j in books:
            recommended_books.append(j)

    return recommended_books
@app.route('/recommend2')
def recommend2():
    book_name = request.args.get('book_name')
    recommended_books = recommend_book(book_name)
    return render_template('recommend2.html', recommended_books=recommended_books)


if __name__ == '__main__':
    app.run(debug=True)