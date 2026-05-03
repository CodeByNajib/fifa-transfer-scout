# fifa-transfer-scout
Explore and analyze FIFA player data through an interactive dashboard with AI-powered insights -  built with Python, FastAPI, Streamlit, Pandas and Matplotlib.

# FIFA Transfer Scout ⚽️

An AI-powered scouting tool that identifies "Hidden Gems" and top talent using FIFA 22 data, FastAPI, and Mistral AI.

##  Features
*   **AI Scout Assistant**: Ask natural language questions about player data using Mistral AI.
*   **Hidden Gem Finder**: Identify undervalued players based on market value vs. overall rating.
*   **Position Analytics**: Discover peak age and average ratings for every position.
*   **Interactive Dashboard**: High-resolution visualizations with automated label positioning to avoid overlap.

##  Tech Stack
*   **Backend**: FastAPI (Python 3.12+).
*   **Frontend**: Streamlit.
*   **AI Engine**: Mistral AI API (RAG-light implementation).
*   **Data Science**: Pandas, Matplotlib, adjustText.
*   **Environment Management**: `uv` (faster than standard pip).

##  Installation & Setup

 1. **Clone the repository**:
   ```bash
   git clone https://github.com/YourUsername/fifa-transfer-scout.git
   cd fifa-transfer-scout



## 2.Set up the environment using uv**:

Bash
uv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
uv pip install -r requirements.txt

Configure Environment Variables:
Create a .env file in the root directory:

MISTRAL_API_KEY=your_actual_key_here


##How to Run
You need to run the backend and frontend simultaneously in two different terminals:

Terminal 1: FastAPI Backend

Bash
uvicorn app.api.main:app --reload
Access API documentation at http://127.0.0.1:8000/docs

Terminal 2: Streamlit Frontend

Bash
streamlit run app/frontend/streamlit_app.py
Access the dashboard at http://localhost:8501

## API Endpoints
GET /players/top/{position}: Get top-rated players.

GET /players/undervalued: Find players with high potential but low cost.

POST /players/ask-scout: Chat with the AI regarding the current dataset.

## Docker Support (Coming Soon)
The project is structured to be containerized using the provided docker-compose.yaml
