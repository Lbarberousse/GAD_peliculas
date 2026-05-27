from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "datasets"


def read_dataset(file_name):
    return pd.read_csv(DATASET_DIR / file_name, sep="\t")


# Leer archivos
fact_movie = read_dataset("fact_movie.csv")
dim_movie = read_dataset("dim_movie.csv")

bridge_movie_actor = read_dataset("bridge_movie_actor.csv")
bridge_movie_crew = read_dataset("bridge_movie_crew.csv")
bridge_movie_genre = read_dataset("bridge_movie_genre.csv")

dim_genre = read_dataset("dim_genre.csv")

# Cantidad de actores por pelicula
actors_by_movie = (
    bridge_movie_actor
    .groupby("movie_key")
    .agg(num_actors=("actor_key", "nunique"))
    .reset_index()
)

# Cantidad de miembros del equipo tecnico por pelicula
crew_by_movie = (
    bridge_movie_crew
    .groupby("movie_key")
    .agg(num_crew_members=("crew_key", "nunique"))
    .reset_index()
)

# Cantidad de generos por pelicula
genres_by_movie = (
    bridge_movie_genre
    .groupby("movie_key")
    .agg(num_genres=("genre_key", "nunique"))
    .reset_index()
)

# Genero principal de cada pelicula
movie_genres = bridge_movie_genre.merge(
    dim_genre,
    on="genre_key",
    how="left",
)

main_genre = (
    movie_genres
    .sort_values(["movie_key", "genre_key"])
    .groupby("movie_key")
    .first()
    .reset_index()[["movie_key", "genre_name"]]
    .rename(columns={"genre_name": "main_genre"})
)

# Construccion de tabla final
tabla_modelo = (
    fact_movie
    .merge(dim_movie[["movie_key", "movie_name"]], on="movie_key", how="left")
    .merge(actors_by_movie, on="movie_key", how="left")
    .merge(crew_by_movie, on="movie_key", how="left")
    .merge(genres_by_movie, on="movie_key", how="left")
    .merge(main_genre, on="movie_key", how="left")
)

# Rellenar valores faltantes
tabla_modelo["num_actors"] = tabla_modelo["num_actors"].fillna(0).astype(int)
tabla_modelo["num_crew_members"] = tabla_modelo["num_crew_members"].fillna(0).astype(int)
tabla_modelo["num_genres"] = tabla_modelo["num_genres"].fillna(0).astype(int)
tabla_modelo["main_genre"] = tabla_modelo["main_genre"].fillna("Unknown")
tabla_modelo["movie_name"] = tabla_modelo["movie_name"].fillna("Unknown")

# Elegir columnas finales
tabla_modelo = tabla_modelo[
    [
        "movie_key",
        "movie_name",
        "release_year",
        "duration_minutes",
        "num_genres",
        "num_actors",
        "num_crew_members",
        "main_genre",
        "rating",
    ]
]

# Guardar CSV final para Altair
output_path = DATASET_DIR / "tabla_modelo_rating.csv"
tabla_modelo.to_csv(output_path, index=False)

print(tabla_modelo.head())
print(f"\nTabla generada en: {output_path}")
