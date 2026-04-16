from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import TrendAnalyzerApp
import json
import os

app = FastAPI(title="TrendSage AI Trend API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global app instance for state persistence (simplified)
analyzer = TrendAnalyzerApp()

class ChatQuery(BaseModel):
    message: str

@app.on_event("startup")
async def startup_event():
    print("🚀 Initializing TrendSage AI Engine...")
    try:
        analyzer.run_pipeline()
        print("✅ Engine ready! Visit http://127.0.0.1:8001 to view the dashboard.")
    except Exception as e:
        print(f"❌ ERROR DURING STARTUP: {e}")
        print("Please ensure you have an active internet connection for the first run to download the ML models.")

@app.get("/")
async def get_dashboard():
    return FileResponse("index.html")

@app.get("/api/trends")
async def get_trends():
    if not analyzer.topic_stats is not None:
        analyzer.run_pipeline()
    
    # Format data for frontend
    topics = []
    for topic, row in analyzer.topic_stats.iterrows():
        topics.append({
            "topic": topic,
            "volume": int(row['volume']),
            "engagement": int(row['engagement']),
            "sentiment": row['sentiment_label'],
            "trend": row['trend_label'],
            "growth": float(row['growth_rate']),
            "summary": row['summary'],
            "platforms": row['platform']
        })
    
    return {
        "topics": topics,
        "insights": analyzer.business_insights
    }

@app.get("/api/refresh")
async def refresh_trends():
    analyzer.run_pipeline()
    return {"status": "success", "message": "Trends and chatbot re-indexed."}

@app.post("/api/chat")
async def chat(query: ChatQuery):
    try:
        if not hasattr(analyzer, 'chatbot') or analyzer.chatbot is None:
            analyzer.run_pipeline()
        response = analyzer.chatbot.get_response(query.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use 127.0.0.1 for more reliable local connection on Windows
    uvicorn.run(app, host="127.0.0.1", port=8001)
