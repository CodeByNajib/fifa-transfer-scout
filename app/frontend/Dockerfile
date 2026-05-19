FROM python:3.14-slim
WORKDIR /app

# 1. Installer uv
RUN pip install uv

# 2. Kopier kun requirements først (for hurtigere caching)
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# EKSTRA: Fortælle Docker præcis, hvor den skal finde streamlit. 
# Når vi installerer pakker med uv pip install --system,
# bliver de installeret i Python-miljøet, men deres "genveje" (executables) lander ofte i /root/.local/bin, 
# som ikke er en del af standard-stien i den slim image
ENV PATH="/root/.local/bin:$PATH"


# 3. Kopier frontend og delte konstanter
# Vi bevarer stien 'app/frontend/', så Streamlit-kommandoen stadig virker
COPY app/frontend/ ./app/frontend
COPY app/api/constants.py ./app/api/constants.py
COPY app/api/utils.py ./app/api/utils.py

# 4. Opsætning
ENV API_URL=http://fastapi:8000

# Vi har IKKE kopieret players_22.csv her, hvilket gør dette image lettere
CMD ["python", "-m", "streamlit", "run", "app/frontend/streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]