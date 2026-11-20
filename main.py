# API AUTENTIX

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import random 
import re
from datetime import datetime

app = FastAPI(title="API Detector de Bots - Dead Internet", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. CARGAR LOS DOS MODELOS
# Modelo 1: B2B
try:
    modelo_b2b = joblib.load("modelo_gam_autentix.pkl")
    MODELO_B2B_CARGADO = True
except Exception as e:
        print(f"ERROR CARGANDO MODELO B2B: {e}")
        MODELO_B2C_CARGADO = False

# Modelo 2: B2C
try:
    modelo_b2c = joblib.load("modelo_gam_b2c.pkl")
    MODELO_B2C_CARGADO = True
except Exception as e:
        print(f"ERROR CARGANDO MODELO B2C: {e}")
        MODELO_B2C_CARGADO = False


# 4. CONTRATOS DE DATOS
# Contrato B2B
class DatosCuentaB2B(BaseModel):
    screen_name: str
    followers_count: int
    following_count: int
    favourites_count: int
    created_at: str
    account_age_days: int
    default_profile_image: bool
    default_profile: bool
    has_description: bool
    description: str
    verified: bool
    has_lang: bool
    lang: str
    location: str
    statuses_count: int
    average_tweets_per_day: float
    geo_enabled: bool
    id: int

# Contrato B2C
class DatosCuentaB2C(BaseModel):
    screen_name: str
    followers_count: int
    following_count: int
    created_at: str
    account_age_days: int
    default_profile_image: bool
    default_profile: bool
    has_description: bool
    description: str
    verified: bool
    has_lang: bool
    lang: str
    location: str
    statuses_count: int
    average_tweets_per_day: float
    geo_enabled: bool
    id: int

def calcular_metricas_temporales(texto_fecha: str, total_posts: int):
    dias_edad = 1000
    media_diaria = 1.5
    if not texto_fecha or texto_fecha.lower() == "desconocida":
        return dias_edad, media_diaria

    meses = {
        "enero": 1, "january": 1, "jan": 1, "febrero": 2, "february": 2, "feb": 2,
        "marzo": 3, "march": 3, "mar": 3, "abril": 4, "april": 4, "apr": 4,
        "mayo": 5, "may": 5, "junio": 6, "june": 6, "jun": 6,
        "julio": 7, "july": 7, "jul": 7, "agosto": 8, "august": 8, "aug": 8,
        "septiembre": 9, "september": 9, "sep": 9, "octubre": 10, "october": 10, "oct": 10,
        "noviembre": 11, "november": 11, "nov": 11, "diciembre": 12, "december": 12, "dec": 12
    }

    try:
        match = re.search(r'(?:en|joined)\s+([a-zA-Z]+)(?:\s+de)?\s+(\d{4})', texto_fecha.lower())
        if match:
            mes_texto = match.group(1)
            anio = int(match.group(2))
            mes_numero = meses.get(mes_texto, 1) 
            fecha_creacion = datetime(anio, mes_numero, 1)
            hoy = datetime.now()
            diferencia = hoy - fecha_creacion
            dias_edad = max(1, diferencia.days) 
            media_diaria = round(total_posts / dias_edad, 2)
    except Exception as e:
        pass

    return dias_edad, media_diaria


# 5. ENDPOINTS

# RUTA 1: PARA STREAMLIT (B2B) 
@app.post("/predict")
def predecir_bot_b2b(datos: DatosCuentaB2B):
    try:
        dias_calculados, media_calculada = calcular_metricas_temporales(datos.created_at, datos.statuses_count)
        datos.account_age_days = dias_calculados
        datos.average_tweets_per_day = media_calculada

        if MODELO_B2B_CARGADO:
            ratio_fol_ing = float(datos.following_count) if datos.followers_count == 0 else datos.following_count / datos.followers_count

            df_entrada = pd.DataFrame([{
                'log_fav': np.log1p(datos.favourites_count),
                'log_fol': np.log1p(datos.followers_count),
                'log_fol_ing': np.log1p(datos.following_count),
                'ratio': ratio_fol_ing,
                'log_tweets': np.log1p(datos.average_tweets_per_day),
                'log_age': np.log1p(datos.account_age_days),
                'default_profile': int(datos.default_profile),
                'default_profile_image': int(datos.default_profile_image),
                'geo_enabled': int(datos.geo_enabled),
                'verified': int(datos.verified),
                'has_description': int(datos.has_description)
            }])

            probabilidad = modelo_b2b.predict_proba(df_entrada)[0] 
            prediccion = 1 if probabilidad > 0.50 else 0 
        else:
            if datos.following_count > (datos.followers_count * 5) or datos.average_tweets_per_day > 50:
                prediccion = 1
                probabilidad = round(random.uniform(0.75, 0.99), 2)
            else:
                prediccion = 0
                probabilidad = round(random.uniform(0.01, 0.45), 2)

        return {
            "prediction_class": int(prediccion),
            "bot_probability": float(probabilidad)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- RUTA 2: PARA LA EXTENSIÓN CHROME (B2C) ---
@app.post("/predict_extension")
def predecir_bot_b2c(datos: DatosCuentaB2C):
    try:
        dias_calculados, media_calculada = calcular_metricas_temporales(datos.created_at, datos.statuses_count)
        datos.account_age_days = dias_calculados
        datos.average_tweets_per_day = media_calculada

        if MODELO_B2C_CARGADO:
            ratio_fol_ing = float(datos.following_count) if datos.followers_count == 0 else datos.following_count / datos.followers_count

            # Aquí NO enviamos 'log_fav' ni 'geo_enabled' al modelo B2C, tal y como decidisteis
            df_entrada = pd.DataFrame([{
                'log_fol': np.log1p(datos.followers_count),
                'log_fol_ing': np.log1p(datos.following_count),
                'ratio': ratio_fol_ing,
                'log_tweets': np.log1p(datos.average_tweets_per_day),
                'log_age': np.log1p(datos.account_age_days),
                'default_profile': int(datos.default_profile),
                'default_profile_image': int(datos.default_profile_image),
                'verified': int(datos.verified),
                'has_description': int(datos.has_description)
            }])

            probabilidad = modelo_b2c.predict_proba(df_entrada)[0] 
            prediccion = 1 if probabilidad > 0.50 else 0 
        else:
            # Simulador para Chrome si el archivo .pkl B2C aún no existe
            if datos.following_count > (datos.followers_count * 5) or datos.average_tweets_per_day > 50:
                prediccion = 1
                probabilidad = round(random.uniform(0.75, 0.99), 2)
            else:
                prediccion = 0
                probabilidad = round(random.uniform(0.01, 0.45), 2)

        return {
            "prediction_class": int(prediccion),
            "bot_probability": float(probabilidad)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def leer_raiz():
    return {"mensaje": "API del Detector de Bots activa y funcionando"}