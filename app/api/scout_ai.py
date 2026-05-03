import os
from mistralai.client import Mistral
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Initialize Mistral client using API key from .env
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


# Sends player context + user question to Mistral and returns the answer
def ask_scout_assistant(question: str, context_df: pd.DataFrame) -> str:
    context = context_df.to_string(index=False, max_rows=20)
    prompt = f"""You are a professional football scout assistent with deep knowledge of player statistics
    You have access to the following FIFA 22 player data:
    
    {context}
    
    Answer the following question based on this data. Be concise and specific. 
    If the answer is not in the data, say so honestly.
    
    Question: {question}
    """
    response = client.chat.complete(
        model="mistral-small-latest", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
