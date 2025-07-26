from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.agents.userproxy_ag import UserProxyAgent
from backend.agents.voicelog_ag import VoiceLogAgent
from backend.agents.datafetch_ag import DataFetcherAgent
from backend.agents.timeanalyze_ag import TimeAnalyzerAgent
from backend.agents.insight_ag import InsightAgent
from backend.agents.coach_ag import CoachAgent
from backend.agents.memory_ag import MemoryAgent
from backend.tools.vector_memory import memory_store
from backend.tools.whisper_transcriber import transcribe_and_tag, extract_activity_insights
import os
import tempfile

app = FastAPI(title="TimeCop API", description="Multi-Agent Productivity System")

# Add CORS middleware - ADD THIS SECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize agents
user_proxy = UserProxyAgent()
voice_logger = VoiceLogAgent()
fetcher = DataFetcherAgent()
analyzer = TimeAnalyzerAgent()
insight = InsightAgent()
coach = CoachAgent()
memory = MemoryAgent()

@app.post("/analyze")
async def analyze_productivity(user_input: str = Form(...), user_id: str = Form(...)):
    """Main productivity analysis endpoint"""
    try:
        # Process user input
        print("user_input:", user_input)
        print("user_id:", user_id)
        processed_input = user_proxy.process_input(user_input)
        print("processed_input:", processed_input)
        all_logs = fetcher.fetch_all_logs(user_id)
        github_data = all_logs["github"]
        calendar_data = all_logs["calendar"]
        email_data = all_logs["email"]
        print("github_data:", github_data)
        # Combine all logs
        combined_logs = {
            "github": github_data,
            "calendar": calendar_data,
            "email": email_data,
            "user_query": processed_input
        }
        
        # Analyze the logs
        analyzed = analyzer.analyze_logs(combined_logs)
        
        # Generate insights
        insights = insight.generate_insights(analyzed)
        
        # Store in RAG memory
        memory_store.store_summary(user_id, insights, "analysis")
        
        # Get coaching advice with historical context
        historical_context = memory_store.query_memory(user_id, user_input)
        coaching = coach.coach(insights.get("analysis", ""), historical_context)
        
        return {
            "status": "success",
            "user_input": processed_input,
            "analysis": analyzed,
            "insights": insights,
            "coaching": coaching,
            "historical_context_used": len(historical_context.split('\n'))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/voice-log")
async def process_voice_log(file: UploadFile, user_id: str = Form(...)):
    """Process voice input and return transcription, tags, insights"""
    # 1. Save the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        # 2. Raw transcription + tagging
        raw = transcribe_and_tag(temp_path)
        # 3. Extract deeper insights
        enriched = extract_activity_insights(raw)
        # 4. Store in memory
        memory_store.store_summary(user_id, enriched, "voice_log")

        # 5. Return a flat schema for React to consume
        return {
            "transcription": enriched["transcription"],
            "tags": {
                "mood":           enriched["mood"],
                "duration":       enriched["duration"],
                "activity_type":  enriched["activity_type"],
                "energy_level":   enriched["energy_level"],
                "confidence":     enriched["confidence"],
            },
            "insight_summary": enriched["insight_summary"],
            "stored_in_memory": True
        }

    except Exception as e:
        # Log the full traceback to console
        import traceback; traceback.print_exc()
        # Return the exception message in the response
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {e}")

@app.get("/memory/{user_id}")
async def get_user_memory(user_id: str, query: str = None, limit: int = 5):
    """Query user's RAG memory"""
    try:
        if query:
            memory_result = memory_store.query_memory(user_id, query, limit)
        else:
            memory_result = memory_store.query_memory(user_id, limit=limit)
        
        trends = memory_store.get_trends(user_id)
        
        return {
            "status": "success",
            "memory": memory_result,
            "trends": trends,
            "query_used": query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory query failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "TimeCop API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)