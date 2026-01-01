import React, { useEffect, useState } from "react";
import MovieCard from "../components/MovieCard";
import "../components/MovieCard.css";

function MovieList({ type = "all" }) {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_URL = process.env.REACT_APP_API_URL;

  const getEndpoint = () => {
    switch (type) {
      case "all":
        return "/movies/all";
      case "trending":
        return "/movies/popular";
      case "upcoming":
        return "/movies/upcoming";
      default:
        return "/movies/all";
    }
  };

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const endpoint = getEndpoint();
        const response = await fetch(`${API_URL}${endpoint}`);
        const data = await response.json();

        if (!Array.isArray(data)) {
          console.error("Backend bir dizi döndürmedi:", data);
          setMovies([]);
        } else {
          setMovies(data);
        }
      } catch (error) {
        console.error("API error:", error);
        setMovies([]);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [API_URL, type]);

  if (loading) return <h2 style={{ color: "white" }}>Loading movies...</h2>;

  return (
    <div className="container">
      <h1 className="page-title">
        🎬 {type === "all" && "Tüm Filmler"}
        {type === "trending" && "Trendler"}
        {type === "upcoming" && "Yakında"}
      </h1>

      <div className="movie-grid">
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            id={movie.id}
            title={movie.title}
            poster_path={movie.poster_path}
            poster_url={movie.poster_url}
            vote_average={movie.vote_average}
            type={type}   // ✔ BURASI ÇOK ÖNEMLİ
          />
        ))}
      </div>
    </div>
  );
}

export default MovieList;
