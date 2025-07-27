from typing import Optional
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.agents.userproxy_ag import UserProxyAgent
from backend.agents.voicelog_ag import VoiceLogAgent
from backend.agents.datafetch_ag import DataFetcherAgent
from backend.agents.timeanalyze_ag import TimeAnalyzerAgent
from backend.agents.insight_ag import InsightAgent
from backend.agents.coach_ag import CoachAgent
from backend.agents.memory_ag import MemoryAgent
from backend.tools import github, google_calendar
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
async def get_user_memory(
    user_id: str,
    query: Optional[str] = None,
    limit: int = 5
):
    try:
        # 1. The flat, line-based output
        memory_text = memory_store.query_memory(user_id, query=query, limit=limit)

        # 2. Trend data
        trends = memory_store.get_trends(user_id)

        # 3. Build the items list from the in‑memory store
        raw_docs = memory_store.memory_store.get(user_id, [])
        recent = raw_docs[-limit:]
        items = []
        for doc in recent:
            content = doc["content"]
            items.append({
                "timestamp": doc["timestamp"],
                "type": doc["type"],
                "llm_summary": content.get("llm_summary"),
                "raw_input": content.get("raw_input"),
            })

        return {
            "status": "success",
            "memory_text": memory_text,
            "trends": trends,
            "query_used": query,
            "items": items
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory query failed: {e}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory query failed: {str(e)}")

@app.get("/dashboard/{user_id}")
async def get_dashboard_analytics(user_id: str):
    """
    Returns three analytics series for the frontend dashboard:
      1. time_distribution: hours per category
      2. focus_trend: last 7 days of deep work hours
      3. context_switches: last 7 days of task switches
    """
    try:
        # 1. Fetch real data
        gh_logs = github.fetch_activity(user_id)
        cal_events = google_calendar.fetch_events(user_id)

        # 2. Build distribution (example logic)
        time_distribution = {
            "Deep Work": sum(1 for e in gh_logs if e.get("action") == "commit"),
            "Meetings": len(cal_events),
            "Distraction": 2,           # replace with real NLP categorization
            "Communication": 3,         # ditto
            "Context Switching": 4      # ditto
        }

        # 3. Build focus trend (mocked, adapt to real timestamps)
        focus_trend = [
            {"date": f"2025-07-{20+i}", "deep_work_hours": 1.5 + (i % 3)}
            for i in range(7)
        ]

        # 4. Build context switches per day (mocked)
        context_switches = [
            {"date": f"2025-07-{20+i}", "switches": 8 + (i * 2 % 5)}
            for i in range(7)
        ]

        return {
            "status": "success",
            "time_distribution": time_distribution,
            "focus_trend": focus_trend,
            "context_switches": context_switches
        }

    except Exception as e:
        raise HTTPException(500, f"Dashboard fetch failed: {e}")
    
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "TimeCop API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)