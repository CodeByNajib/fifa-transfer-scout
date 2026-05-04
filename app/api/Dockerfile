FROM python:3.14-slim
WORKDIR /app

# 1. Installer uv
RUN pip install uv

# 2. Kopier requirements og installer
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Fortælle Docker præcis, hvor den skal finde streamlit. 
# Når vi installerer pakker med uv pip install --system,
# bliver de installeret i Python-miljøet, men deres "genveje" (executables) lander ofte i /root/.local/bin, 
# som ikke er en del af standard-stien i den slim image
ENV PATH="/root/.local/bin:$PATH"

# 3. Kopier backend-mappen og data-filen
COPY app/api/ ./app/api/
COPY app/api/players_22.csv .

# 4. Start serveren
CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
