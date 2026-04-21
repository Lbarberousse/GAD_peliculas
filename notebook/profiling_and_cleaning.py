import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================

MOVIES_PATH = "data/raw/movies.csv"
CREW_PATH = "data/raw/crew.csv"
GENRES_PATH = "data/raw/genres.csv"
ACTORS_PATH = "data/raw/actors.csv"

OUTPUT_MOVIES_CLEAN = "data/clean/movies_clean.csv"
OUTPUT_CREW_CLEAN = "data/clean/crew_clean.csv"
OUTPUT_GENRES_CLEAN = "data/clean/genres_clean.csv"
OUTPUT_ACTORS_CLEAN = "data/clean/actors_clean.csv"

# =========================
# FUNCIONES AUXILIARES
# =========================

def print_shape_info(dfs: dict):
    print("\n=== DIMENSIONES DE LOS DATASETS ===")
    for nombre, df in dfs.items():
        filas, columnas = df.shape
        print(f"{nombre}:")
        print(f"  Nro de filas: {filas}")
        print(f"  Nro de columnas: {columnas}\n")


def analizar_duplicados(df, nombre_df):
    duplicados = {}
    for col in df.columns:
        duplicados[col] = df[col].duplicated(keep=False).sum()

    df_duplicados = pd.DataFrame(
        list(duplicados.items()),
        columns=["Columna", "Nro Duplicados"]
    )

    df_duplicados["% Duplicados"] = (
        df_duplicados["Nro Duplicados"] / len(df) * 100
    ).round(2)

    df_duplicados = df_duplicados.sort_values(by="% Duplicados", ascending=False)

    print(f"\n=== DUPLICADOS EN {nombre_df.upper()} ===")
    print(df_duplicados.to_string(index=False))


def analizar_unicos(df, nombre_df):
    unicos = {}
    for col in df.columns:
        unicos[col] = df[col].nunique(dropna=True)

    df_unicos = pd.DataFrame(
        list(unicos.items()),
        columns=["Columna", "Nro Valores Unicos"]
    )

    df_unicos = df_unicos.sort_values(by="Nro Valores Unicos", ascending=False)

    print(f"\n=== VALORES ÚNICOS EN {nombre_df.upper()} ===")
    print(df_unicos.to_string(index=False))


def analizar_nulos(df, nombre_df):
    nulls = df.isna().sum().reset_index()
    nulls.columns = ["Columna", "Nro de Nulos"]

    nulls["% Nulos"] = (nulls["Nro de Nulos"] / len(df) * 100).round(2)
    nulls = nulls.sort_values(by="% Nulos", ascending=False)

    print(f"\n=== NULOS EN {nombre_df.upper()} ===")
    print(nulls.to_string(index=False))


def perfilar_dataset(df, nombre_df):
    analizar_duplicados(df, nombre_df)
    analizar_unicos(df, nombre_df)
    analizar_nulos(df, nombre_df)


# =========================
# PLOTS
# =========================

def plot_rating(df_movie):
    data = df_movie["rating"].dropna()

    plt.figure()
    plt.hist(data, bins=20, density=True, alpha=0.6)
    data.plot(kind="kde", linewidth=2)

    plt.title("Distribución de Rating")
    plt.xlabel("Rating")
    plt.ylabel("Densidad")
    plt.grid(True)
    plt.show()


def plot_duration(df_movie):
    data = df_movie["minute"].dropna()
    data = data[(data > 0) & (data <= 500)]

    plt.figure()
    plt.hist(data, bins=30, alpha=0.7)

    plt.title("Duración de películas")
    plt.xlabel("Minutos")
    plt.ylabel("Cantidad")
    plt.grid(True)
    plt.show()


def plot_top_actors(df_actors):
    top = df_actors["name"].value_counts().head(10)

    plt.figure()
    top.plot(kind="bar")

    plt.title("Top 10 actores con más participaciones")
    plt.xlabel("Actor")
    plt.ylabel("Cantidad de películas")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()


# =========================
# LIMPIEZA
# =========================

def limpiar_movies(df):
    df = df.copy()

    df["minute"] = pd.to_numeric(df["minute"], errors="coerce")
    df["date"] = pd.to_numeric(df["date"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    df = df[
        (df["minute"] > 0) &
        (df["minute"] < 300) &
        (df["date"].notna()) &
        (df["name"].notna())
    ]

    columnas_drop = [c for c in ["description", "tagline"] if c in df.columns]
    df = df.drop(columns=columnas_drop)

    return df


def limpiar_crew(df):
    df = df.copy()

    df = df[df["name"].notna()]
    df = df.rename(columns={"name": "member_name"})

    roles_validos = ["Director", "Producer", "Casting", "Art Direction"]
    df = df[df["role"].isin(roles_validos)]

    return df


def limpiar_genres(df):
    return df.copy()


def limpiar_actors(df):
    df = df.copy()

    df = df[df["name"].notna()]
    df = df[df["role"].notna()]

    df["name"] = df["name"].str.strip()

    return df


# =========================
# MAIN
# =========================

def main():
    Path("data/clean").mkdir(parents=True, exist_ok=True)

    # Carga
    df_movie = pd.read_csv(MOVIES_PATH)
    df_crew = pd.read_csv(CREW_PATH)
    df_genres = pd.read_csv(GENRES_PATH)
    df_actors = pd.read_csv(ACTORS_PATH)

    dfs = {
        "movies": df_movie,
        "crew": df_crew,
        "genres": df_genres,
        "actors": df_actors
    }

    print_shape_info(dfs)

    # ===== PROFILING RAW =====
    perfilar_dataset(df_movie, "movies_raw")

    plot_rating(df_movie)
    plot_duration(df_movie)

    perfilar_dataset(df_actors, "actors_raw")
    perfilar_dataset(df_crew, "crew_raw")
    perfilar_dataset(df_genres, "genres_raw")

    plot_top_actors(df_actors)

    # ===== LIMPIEZA =====
    df_movie_clean = limpiar_movies(df_movie)
    df_crew_clean = limpiar_crew(df_crew)
    df_genres_clean = limpiar_genres(df_genres)
    df_actors_clean = limpiar_actors(df_actors)

    # ===== GUARDADO =====
    df_movie_clean.to_csv(OUTPUT_MOVIES_CLEAN, index=False)
    df_crew_clean.to_csv(OUTPUT_CREW_CLEAN, index=False)
    df_genres_clean.to_csv(OUTPUT_GENRES_CLEAN, index=False)
    df_actors_clean.to_csv(OUTPUT_ACTORS_CLEAN, index=False)

    # ===== PROFILING CLEAN =====
    perfilar_dataset(df_movie_clean, "movies_clean")
    perfilar_dataset(df_actors_clean, "actors_clean")
    perfilar_dataset(df_crew_clean, "crew_clean")
    perfilar_dataset(df_genres_clean, "genres_clean")

    print("\n Datos limpiados guardados correctamente.")


if __name__ == "__main__":
    main()
