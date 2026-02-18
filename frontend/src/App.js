import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const OMDB_API_KEY = "7c18b116";

function App() {
  const [mode, setMode] = useState("user");
  const [input, setInput] = useState("");
  const [movies, setMovies] = useState([]);

  const getRecommendations = async () => {
    try {
      let response;

      if (mode === "user") {
        response = await axios.get(
          `http://127.0.0.1:5000/recommend?user_id=${input}`
        );
      } else {
        response = await axios.get(
          `http://127.0.0.1:5000/recommend_movie?movie_name=${input}`
        );
      }

      const recommendedTitles = response.data;

      const moviesWithPosters = await Promise.all(
        recommendedTitles.map(async (fullTitle) => {
          const cleanTitle = fullTitle
            .replace(/\(\d{4}\)/, "")
            .trim();

          const omdbResponse = await axios.get(
            `https://www.omdbapi.com/?t=${encodeURIComponent(
              cleanTitle
            )}&apikey=${OMDB_API_KEY}`
          );

          return {
            title: fullTitle,
            poster:
              omdbResponse.data.Poster &&
              omdbResponse.data.Poster !== "N/A"
                ? omdbResponse.data.Poster
                : null,
          };
        })
      );

      setMovies(moviesWithPosters);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="app">
      <h1>🎬 Hybrid Movie Recommendation System</h1>

      <div>
        <button onClick={() => setMode("user")}>By User</button>
        <button onClick={() => setMode("movie")}>By Movie</button>
      </div>

      <input
        type="text"
        placeholder={
          mode === "user"
            ? "Enter User ID"
            : "Enter Exact Movie Name"
        }
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button onClick={getRecommendations}>
        Get Recommendations
      </button>

      <div className="movie-grid">
        {movies.map((movie, index) => (
          <div className="movie-card" key={index}>
            {movie.poster ? (
              <img src={movie.poster} alt={movie.title} />
            ) : (
              <div className="no-image">No Image</div>
            )}
            <h3>{movie.title}</h3>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
