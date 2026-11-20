# AutentiX
**Detección Avanzada de Cuentas Automatizadas (Bots) en X (Twitter) mediante Machine Learning.**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit)
![Chrome Extension](https://img.shields.io/badge/Chrome_Extension-4285F4?style=flat&logo=google-chrome)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-GAM-orange.svg)

## Descripción del Proyecto
AutentiX es un sistema de auditoría de perfiles en la red social X (anteriormente Twitter) diseñado para clasificar cuentas como **humanas** o **automatizadas (bots)**. 

El proyecto presenta una **arquitectura cliente-servidor basada en el desacoplamiento**, garantizando que el procesamiento analítico y matemático opere de forma centralizada y segura. Este diseño asegura una alta escalabilidad y facilita el mantenimiento técnico de las interfaces frente a futuras actualizaciones.

---

## Arquitectura y Componentes

El ecosistema de AutentiX se divide en tres componentes principales:

### 1. Motor Central: API RESTful (Backend)
El núcleo del sistema está construido sobre **FastAPI**. Actúa como el motor que gestiona las peticiones HTTP y conecta las interfaces con nuestro modelo predictivo serializado (`.pkl`).
* **Eficiencia Asíncrona:** Alta capacidad para procesar múltiples peticiones sin cuellos de botella.
* **Integridad de Datos:** Implementa esquemas de validación estrictos mediante **Pydantic**.
* **Doble Endpoint:** Cuenta con dos rutas de inferencia optimizadas: una para el modelo B2B complejo y otra más ligera para la extensión B2C.

### 2. Panel Web Corporativo (B2B)
Una aplicación analítica desarrollada en **Streamlit** pensada para empresas y consultoras de redes sociales.
* **Procesamiento Masivo:** Auditoría por lotes mediante la carga de archivos `CSV`.
* **Umbral Dinámico:** Permite al cliente ajustar su propio nivel de exigencia (sensibilidad) para marcar perfiles como bots.
* **Entregables:** Generación de informes ejecutivos en `PDF` y descarga de datasets clasificados y filtrados.

### 3. Extensión B2C (Frontend)
Una extensión para **Google Chrome** diseñada para auditar perfiles en tiempo real de forma amigable e intuitiva.
* **Web Scraping Inteligente:** Elimina la dependencia y los costes de la API oficial de X analizando directamente el código fuente.
* **Eficiencia y Accesibilidad:** Capitaliza la estructura semántica de los datos destinados a lectores de pantalla (etiquetas ARIA), extrayendo la información de manera no intrusiva.
* **Veredicto Visual:** Interfaz simple mediante un pop-up que utiliza indicadores en verde (humano) y rojo (bot).

---

## Stack Tecnológico

* **Backend & API:** Python, FastAPI, Pydantic, Uvicorn.
* **Machine Learning:** Scikit-Learn, pyGAM (Modelos Aditivos Generalizados), Pandas, NumPy.
* **Aplicación B2B:** Streamlit, ReportLab (para generación de PDFs).
* **Extensión B2C:** JavaScript (ES6), HTML5, CSS3, Chrome Extensions API.

---

## Instalación y Despliegue (Local)

### 1. Levantar la API Central
```bash
# Clonar el repositorio
git clone https://github.com/clauu-uni/x-bot-detector.git
cd x-bot-detector

# Crear entorno virtual e instalar dependencias
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
pip install -r requirements_api.txt

# Ejecutar el servidor (por defecto en http://localhost:8000)
uvicorn api_main:app --reload
```

### 2. Levantar la Aplicación Web (B2B)
```bash
# En una nueva terminal, instalar dependencias del frontend
pip install -r requirements_web.txt

# Ejecutar la aplicación de Streamlit
streamlit run dashboard.py
```

### 3. Instalar la Extensión de Chrome (B2C)
1. Abre Google Chrome y ve a `chrome://extensions/`.
2. Activa el **Modo de desarrollador** (arriba a la derecha).
3. Haz clic en **Cargar descomprimida**.
4. Selecciona la carpeta `extension_chrome` de este repositorio.

---

## Dataset de Prueba
En la carpeta `/data` puedes encontrar un archivo de prueba llamado `dataset_auditoria_b2b.csv` ya formateado y listo para ser cargado en el panel de Streamlit y probar el procesamiento masivo.

---

## Autores
* **Claudia Ruiz García** - Desarrollo de la API e Interfaces. - https://www.linkedin.com/in/claudia-ruiz-garcia/
* **Lara Ruiz Casado** - Desarrollo del modelo de ML.
* **Danielle Saxon** - Desarrollo del modelo de ML.
* **Vega Montalbán Mengod** - Desarrollo de la Interfaz Web.
* **Juan José Escriche Giménez** - Limpieza y depuración del DataSet.
* Proyecto académico desarrollado para la **Universitat Politècnica de València (UPV)**.
