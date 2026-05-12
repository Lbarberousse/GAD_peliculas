# Implementacion de Superset con Dremio

Este proyecto usa Superset como herramienta de visualizacion, pero la fuente de datos para Superset debe ser Dremio. El flujo queda asi:

```text
CSV limpios -> MinIO -> Dremio/Nessie -> Superset
```

## 1. Levantar los servicios

Desde la raiz del proyecto:

```powershell
docker compose up -d
```

Servicios principales:

- Dremio: http://localhost:9047
- Superset: http://localhost:8082
- MinIO: http://localhost:9001
- pgAdmin: http://localhost:8081

## 2. Preparar Dremio

1. Entrar a http://localhost:9047.
2. Crear o usar el usuario administrador de Dremio.
3. Verificar que exista la fuente `Minio`.
4. Verificar que los archivos limpios esten disponibles en:

```text
Minio.clean.movies_clean.csv
Minio.clean.actors_clean.csv
Minio.clean.genres_clean.csv
Minio.clean.crew_clean.csv
```

5. Ejecutar en Dremio el script:

```text
dremio/create_gold_direct_from_minio.sql
```

Al final deben existir estas tablas:

```text
nessie.modelado.dim_movie
nessie.modelado.dim_actor
nessie.modelado.dim_genre
nessie.modelado.dim_crew
nessie.modelado.fact_movies
nessie.modelado.bridge_movie_actor
nessie.modelado.bridge_movie_genre
nessie.modelado.bridge_movie_crew
```

## 3. Conectar Superset a Dremio

1. Entrar a http://localhost:8082.
2. Ir a `Settings > Database Connections`.
3. Crear una nueva conexion.
4. Elegir `Other` o `Dremio`, segun aparezca en la imagen.
5. Usar esta SQLAlchemy URI:

```text
dremio://USUARIO_DREMIO:PASSWORD_DREMIO@dremio:31010/dremio
```

Ejemplo:

```text
dremio://admin:password@dremio:31010/dremio
```

Importante: dentro de Docker se usa `dremio` como host, no `localhost`.

## 4. Crear datasets en Superset

En Superset:

1. Ir a `Datasets`.
2. Crear datasets usando la conexion de Dremio.
3. Seleccionar el esquema/catalogo `nessie.modelado`.
4. Agregar las tablas principales:

```text
fact_movies
dim_movie
dim_actor
dim_genre
dim_crew
bridge_movie_actor
bridge_movie_genre
bridge_movie_crew
```

## 5. Vistas recomendadas para dashboards

Para Superset suele ser mas comodo crear vistas analiticas en Dremio y usarlas como datasets. Por ejemplo:

```sql
CREATE VIEW nessie.modelado.v_movies_by_year AS
SELECT
  release_year,
  COUNT(*) AS total_movies,
  AVG(rating) AS avg_rating,
  AVG(duration_minutes) AS avg_duration
FROM nessie.modelado.fact_movies
GROUP BY release_year;
```

```sql
CREATE VIEW nessie.modelado.v_movies_by_genre AS
SELECT
  g.genre_name,
  COUNT(*) AS total_movies,
  AVG(f.rating) AS avg_rating
FROM nessie.modelado.fact_movies f
JOIN nessie.modelado.bridge_movie_genre bg
  ON f.movie_key = bg.movie_key
JOIN nessie.modelado.dim_genre g
  ON bg.genre_key = g.genre_key
GROUP BY g.genre_name;
```

```sql
CREATE VIEW nessie.modelado.v_top_actors AS
SELECT
  a.actor_name,
  COUNT(*) AS total_movies
FROM nessie.modelado.bridge_movie_actor ba
JOIN nessie.modelado.dim_actor a
  ON ba.actor_key = a.actor_key
GROUP BY a.actor_name;
```

Estas vistas permiten armar graficos en Superset sin repetir joins en cada chart.

