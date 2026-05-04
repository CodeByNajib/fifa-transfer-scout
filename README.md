# FIFA Transfer Scout

Explore and analyze FIFA player data through an interactive dashboard with AI-powered insights. This project identifies "Hidden Gems" and top talent using FIFA 22 data, FastAPI, and Mistral AI, demonstrating a full-stack integration of data science, DevOps, and Large Language Models (LLM).
![FIFA Transfer Scout Logo](FIFA_Transfer_Scout.png)

## Features

- **AI Scout Assistant:** Ask natural language questions about player data using Mistral AI (RAG-light).
- **Hidden Gem Finder:** Identify undervalued players based on market value vs. overall rating.
- **World Map Distribution:** Visual exploration of player nationalities using GeoPandas.
- **Career Peak Analytics:** Discover peak age and average ratings per position.
- **Dockerized Architecture:** Fully containerized microservices (API + Frontend).

## Tech Stack

- **Backend:** FastAPI (Python 3.12)
- **Frontend:** Streamlit
- **AI Engine:** Mistral AI API
- **DevOps:** Docker, Docker Compose, uv (fast package manager)
- **Data Science:** NumPy, Pandas, Matplotlib, GeoPandas

## Quick Start with Docker (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/CodeByNajib/fifa-transfer-scout.git
cd fifa-transfer-scout
```

2. Configure environment variables — create a `.env` file in the root directory:
MISTRAL_API_KEY=your_actual_key_here
FOOTBALL_DATA_API_KEY=your_actual_key_here

3. Spin up the containers:

```bash
docker compose up --build
```

- Dashboard: `http://localhost:8501`
- API Docs: `http://localhost:8000/docs`

## Manual Setup (Local Development)

1. Set up the environment:

```bash
uv venv venv
source venv/bin/activate
uv pip install -r requirements.txt
```

2. Run backend (Terminal 1):

```bash
uvicorn app.api.main:app --reload
```

3. Run frontend (Terminal 2):

```bash
streamlit run app/frontend/streamlit_app.py
```

## Project Structure

```
.
├── app/
│   ├── api/          # FastAPI backend & data module
│   ├── frontend/     # Streamlit dashboard
│   └── tests/        # Pytest suite
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API Endpoints

- `GET /players/top/{position}` - Get top-rated players by position
- `GET /players/undervalued` - Find high quality, low cost players
- `GET /players/peak-age` - Get peak age statistics per position
- `POST /players/ask-scout` - Chat with the AI scout assistant
- `GET /transfers/news` - Fetch live transfer news from external API
