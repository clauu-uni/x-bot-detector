import pandas as pd
import numpy as np
from pygam import LogisticGAM, s, f
import joblib

# 1. Cargar el dataset (¡Asegúrate de usar el de B2C!)
print("Cargando datos B2C...")
datos_b2c = pd.read_csv("datos_b2b.csv")

# 2. Replicar las transformaciones matemáticas excluyendo geo_enabled y likes
print("Aplicando transformaciones log1p y filtrando variables B2C...")
X = pd.DataFrame()

# Variables continuas
X['log_fol'] = np.log1p(datos_b2c['followers_count'])
X['log_fol_ing'] = np.log1p(datos_b2c['following_count'])
X['ratio'] = datos_b2c['ratio_following_followers']
X['log_tweets'] = np.log1p(datos_b2c['average_tweets_per_day'])
X['log_age'] = np.log1p(datos_b2c['account_age_days'])

# Variables categóricas/booleanas (convertidas a 0 y 1)
X['default_profile'] = datos_b2c['default_profile'].astype(int)
X['default_profile_image'] = datos_b2c['default_profile_image'].astype(int)
X['verified'] = datos_b2c['verified'].astype(int)
X['has_description'] = datos_b2c['has_description'].astype(int)
# NOTA: Omitimos deliberadamente geo_enabled y favourites_count.

# Variable objetivo
y = datos_b2c['is_bot'].astype(int)

# 3. Definir la estructura del GAM para el B2C (9 variables en total)
print("Entrenando el modelo GAM B2C...")
modelo_gam_b2c = LogisticGAM(
    s(0) + s(1) + s(2) + s(3) + s(4) +  # Las 5 primeras son continuas (s)
    f(5) + f(6) + f(7) + f(8)           # Las 4 últimas son booleanas (f)
)

# Entrenar el modelo
modelo_gam_b2c.fit(X, y)
print("¡Modelo entrenado con éxito!")

# 4. Exportar el modelo a .pkl
nombre_archivo = 'modelo_gam_b2c.pkl'
joblib.dump(modelo_gam_b2c, nombre_archivo)
print(f"¡ÉXITO! Modelo exportado como '{nombre_archivo}'. Ponlo en la misma carpeta que tu API.")
