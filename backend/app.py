import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches

tmdb = pd.read_csv("https://drive.google.com/uc?id=1do5L9VIoyDHHu9lzTHyFdrbyhCwHJ11K")
imdb = pd.read_csv("https://drive.google.com/uc?id=1JI_JtNZ2i1Mtfpubo02F6TnN4Q2dFxQh")

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

ratings = pd.merge(ratings, movies[["movie_id", "title"]], on="movie_id")

user_movie_matrix = ratings.pivot_table(
    index="user_id",
    columns="title",
    values="rating"
).fillna(0)

user_similarity = cosine_similarity(user_movie_matrix)

movie_movie_matrix = user_movie_matrix.T
movie_similarity = cosine_similarity(movie_movie_matrix)

movie_similarity_df = pd.DataFrame(
    movie_similarity,
    index=movie_movie_matrix.index,
    columns=movie_movie_matrix.index
)

def recommend_movies(user_id, n=5):
    similarity_scores = user_similarity[user_id - 1]
    similar_users = similarity_scores.argsort()[::-1][1:11]
    recommended = user_movie_matrix.iloc[similar_users].mean()
    user_rated = user_movie_matrix.iloc[user_id - 1]
    recommended = recommended[user_rated == 0]
    top_movies = recommended.sort_values(ascending=False).head(n).index.tolist()
    return top_movies

def find_closest_movie(name):
    movie_titles = movie_similarity_df.index.tolist()
    matches = get_close_matches(name, movie_titles, n=1, cutoff=0.4)
    return matches[0] if matches else None

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Backend is running successfully!"

@app.route("/recommend", methods=["GET"])
def recommend():
    user_id = int(request.args.get("user_id"))
    recommendations = recommend_movies(user_id)
    return jsonify(recommendations)

@app.route("/recommend_movie", methods=["GET"])
def recommend_movie():
    movie_name = request.args.get("movie_name")
    if not movie_name:
        return jsonify({"error": "Please provide movie_name"})
    closest_movie = find_closest_movie(movie_name)
    if not closest_movie:
        return jsonify({"error": "Movie not found"})
    similar_scores = movie_similarity_df[closest_movie].sort_values(ascending=False)
    similar_movies = similar_scores.iloc[1:6].index.tolist()
    return jsonify({
        "searched": movie_name,
        "matched": closest_movie,
        "recommendations": similar_movies
    })

if __name__ == "__main__":
    app.run(debug=True)
