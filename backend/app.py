import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)


# Loading datasets


ratings = pd.read_csv(
    "u.data",
    sep="\t",
    names=["user_id", "movie_id", "rating", "timestamp"]
)

movie_columns = [
    "movie_id", "title", "release_date", "video_release_date",
    "IMDb_URL", "unknown", "Action", "Adventure", "Animation",
    "Children", "Comedy", "Crime", "Documentary", "Drama",
    "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery",
    "Romance", "Sci-Fi", "Thriller", "War", "Western"
]

movies = pd.read_csv(
    "u.item",
    sep="|",
    encoding="latin-1",
    names=movie_columns
)


# Merge ratings with movie titles

ratings = pd.merge(ratings, movies[["movie_id", "title"]], on="movie_id")


# Create User-Movie Matrix


user_movie_matrix = ratings.pivot_table(
    index="user_id",
    columns="title",
    values="rating"
).fillna(0)

# User-Based Similarity


user_similarity = cosine_similarity(user_movie_matrix)


# Movie-Based Similarity


movie_movie_matrix = user_movie_matrix.T
movie_similarity = cosine_similarity(movie_movie_matrix)

movie_similarity_df = pd.DataFrame(
    movie_similarity,
    index=movie_movie_matrix.index,
    columns=movie_movie_matrix.index
)


# User Recommendation Function


def recommend_movies(user_id, n=5):
    similarity_scores = user_similarity[user_id - 1]
    similar_users = similarity_scores.argsort()[::-1][1:11]

    recommended = user_movie_matrix.iloc[similar_users].mean()
    user_rated = user_movie_matrix.iloc[user_id - 1]
    recommended = recommended[user_rated == 0]

    top_movies = recommended.sort_values(ascending=False).head(n).index.tolist()

    return top_movies



# Home Route


@app.route("/")
def home():
    return "Backend is running successfully!"



# User-Based API


@app.route("/recommend", methods=["GET"])
def recommend():
    user_id = int(request.args.get("user_id"))
    recommendations = recommend_movies(user_id)
    return jsonify(recommendations)



# Movie-Based API


@app.route("/recommend_movie", methods=["GET"])
def recommend_movie():
    movie_name = request.args.get("movie_name")

    if movie_name not in movie_similarity_df.index:
        return jsonify(["Movie not found in dataset"])

    similar_scores = movie_similarity_df[movie_name].sort_values(ascending=False)
    similar_movies = similar_scores.iloc[1:6].index.tolist()

    return jsonify(similar_movies)



# Run App


if __name__ == "__main__":
    app.run(debug=True)
