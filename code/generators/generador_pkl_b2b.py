import pandas as pd
import numpy as np
from pygam import LogisticGAM, s, f
import joblib

# 1. Cargar el dataset (asegúrate de que la ruta es correcta)
print("Cargando datos...")
datos_b2b = pd.read_csv("datos_b2b.csv")

# 2. Replicar las transformaciones matemáticas de R (log1p)
print("Aplicando transformaciones log1p...")
X = pd.DataFrame()
X['log_fav'] = np.log1p(datos_b2b['favourites_count'])
X['log_fol'] = np.log1p(datos_b2b['followers_count'])
X['log_fol_ing'] = np.log1p(datos_b2b['following_count'])
X['ratio'] = datos_b2b['ratio_following_followers']
X['log_tweets'] = np.log1p(datos_b2b['average_tweets_per_day'])
X['log_age'] = np.log1p(datos_b2b['account_age_days'])

# Las variables booleanas/categóricas se pasan a enteros (0 y 1)
X['default_profile'] = datos_b2b['default_profile'].astype(int)
X['default_profile_image'] = datos_b2b['default_profile_image'].astype(int)
X['geo_enabled'] = datos_b2b['geo_enabled'].astype(int)
X['verified'] = datos_b2b['verified'].astype(int)
X['has_description'] = datos_b2b['has_description'].astype(int)

# Variable objetivo (asegúrate de que la columna se llama así en tu CSV)
y = datos_b2b['is_bot'].astype(int)

# 3. Definir la estructura del GAM en Python
# s() es para variables continuas (con splines) y f() para categóricas/factores
# Los números (0, 1, 2...) corresponden a las columnas de X en orden.
print("Entrenando el modelo GAM...")
modelo_gam = LogisticGAM(
    s(0) + s(1) + s(2) + s(3) + s(4) + s(5) +  # Variables continuas con log1p y ratio
    f(6) + f(7) + f(8) + f(9) + f(10)          # Variables booleanas/categóricas
)

# Entrenar el modelo
modelo_gam.fit(X, y)
print("¡Modelo entrenado con éxito!")

# 4. Exportar el modelo a .pkl
nombre_archivo = 'modelo_gam_autentix.pkl'
joblib.dump(modelo_gam, nombre_archivo)
print(f"¡ÉXITO! Modelo exportado como '{nombre_archivo}'. Ya puedes llevarlo a tu FastAPI.")
