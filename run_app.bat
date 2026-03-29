@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Bedrock AI App...
echo Open your browser to http://localhost:8501
streamlit run bedrock_ai_app.py