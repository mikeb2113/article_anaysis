from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Sentiment Analysis API"}

@app.get("/run-analysis")
async def run_sentiment_analysis():
    """Run sentiment_analysis.py as a subprocess and return output."""
    try:
        result = subprocess.run(["python3", "sentiment_analysis.py"], capture_output=True, text=True)
        return {"status": "Success", "output": result.stdout}
    except Exception as e:
        return {"status": "Error", "message": str(e)}