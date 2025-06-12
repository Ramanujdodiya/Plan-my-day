from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import httpx
import json
from datetime import datetime, timedelta
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import openai

# --- Configuration ---
app = FastAPI(title="PlanMyDay API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.planmyday
venues_collection = db.venues
plans_collection = db.day_plans

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'YOUR_WEATHER_API_KEY_HERE')

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY


# --- Pydantic Models ---

class Location(BaseModel):
    lat: float
    lng: float
    address: str

class PlanRequest(BaseModel):
    location: Location
    budget: int
    interests: List[str]
    duration: str
    group_size: int = 1

class Venue(BaseModel):
    id: str
    name: str
    category: str
    location: Location
    price_range: str
    rating: float
    description: str
    popular_items: List[str] = []
    opening_hours: str
    estimated_duration: int
    booking_url: Optional[str] = None

class WeatherData(BaseModel):
    temperature: float
    description: str
    feels_like: float
    humidity: int
    weather_main: str

class ItineraryItem(BaseModel):
    venue: Venue
    start_time: str
    end_time: str
    notes: str = ""

class DayPlan(BaseModel):
    id: str
    location: Location
    date: str
    weather: WeatherData
    total_budget: int
    estimated_cost: int
    itinerary: List[ItineraryItem]
    created_at: datetime


# --- Sample Data and Initialization ---

SAMPLE_VENUES = [
    {
        "id": str(uuid.uuid4()), "name": "The Coffee Corner", "category": "restaurant",
        "location": {"lat": 40.7589, "lng": -73.9851, "address": "123 Broadway, NYC"},
        "price_range": "$$", "rating": 4.5, "description": "Cozy coffee shop", "opening_hours": "7:00 AM - 6:00 PM", "estimated_duration": 45
    },
    {
        "id": str(uuid.uuid4()), "name": "Central Park", "category": "attraction",
        "location": {"lat": 40.7821, "lng": -73.9654, "address": "Central Park, NYC"},
        "price_range": "$", "rating": 4.8, "description": "Iconic urban park", "opening_hours": "6:00 AM - 1:00 AM", "estimated_duration": 120
    }
]

async def init_sample_data():
    if await venues_collection.count_documents({}) == 0:
        await venues_collection.insert_many(SAMPLE_VENUES)
        print("Sample venues initialized.")

@app.on_event("startup")
async def startup_event():
    await init_sample_data()


# --- Core Services ---

class WeatherService:
    @staticmethod
    async def get_current_weather(lat: float, lng: float) -> WeatherData:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lng, "appid": WEATHER_API_KEY, "units": "metric"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                return WeatherData(
                    temperature=data["main"]["temp"],
                    description=data["weather"][0]["description"],
                    feels_like=data["main"]["feels_like"],
                    humidity=data["main"]["humidity"],
                    weather_main=data["weather"][0]["main"],
                )
        except Exception as e:
            print(f"Weather API error: {e}. Returning fallback data.")
            return WeatherData(temperature=22.0, description="partly cloudy", feels_like=24.0, humidity=65, weather_main="Clouds")

class AIPlanner:
    @staticmethod
    async def generate_itinerary(request: PlanRequest, weather: WeatherData, venues: List[Dict]) -> List[ItineraryItem]:
        try:
            venue_info = "\n".join([f"- {v['name']} ({v['category']}): {v['description']}" for v in venues[:15]])
            system_prompt = "You are an expert day planner..."
            user_prompt = f"Create a detailed day plan for {request.location.address}..."
            
            response = await openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            ai_data = json.loads(response.choices[0].message.content)
            itinerary_items = []
            
            for item in ai_data.get("itinerary", []):
                venue_match = next((v for v in venues if v["name"].lower() in item["venue_name"].lower()), None)
                if venue_match:
                    itinerary_items.append(ItineraryItem(
                        venue=Venue(**venue_match),
                        start_time=item.get("start_time", "N/A"),
                        end_time=item.get("end_time", "N/A"),
                        notes=item.get("notes", "")
                    ))
            return itinerary_items

        except Exception as e:
            print(f"AI planning error: {e}. Switching to fallback.")
            return await AIPlanner.fallback_planning(request, weather, venues)
    
    @staticmethod
    async def fallback_planning(request: PlanRequest, weather: WeatherData, venues: List[Dict]) -> List[ItineraryItem]:
        suitable_venues = sorted(venues, key=lambda x: x['rating'], reverse=True)[:5]
        itinerary = []
        current_time = datetime.strptime("09:00", "%H:%M")
        
        for venue_data in suitable_venues:
            start_time_obj = current_time
            end_time_obj = start_time_obj + timedelta(minutes=venue_data['estimated_duration'])
            itinerary.append(ItineraryItem(
                venue=Venue(**venue_data),
                start_time=start_time_obj.strftime("%H:%M"),
                end_time=end_time_obj.strftime("%H:%M"),
                notes="A great choice."
            ))
            current_time = end_time_obj + timedelta(minutes=30)
        return itinerary


# --- API Endpoints ---

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/plan")
async def create_day_plan(request: PlanRequest):
    try:
        weather = await WeatherService.get_current_weather(request.location.lat, request.location.lng)
        venues = await venues_collection.find({}).to_list(100)
        itinerary = await AIPlanner.generate_itinerary(request, weather, venues)
        
        if not itinerary:
            raise HTTPException(status_code=500, detail="Failed to generate itinerary.")

        price_map = {"$": 25, "$$": 50, "$$$": 100, "$$$$": 150}
        estimated_cost = sum(price_map.get(item.venue.price_range, 0) for item in itinerary)
        
        day_plan = DayPlan(
            id=str(uuid.uuid4()),
            location=request.location,
            date=datetime.now().strftime("%Y-%m-%d"),
            weather=weather,
            total_budget=request.budget,
            estimated_cost=estimated_cost,
            itinerary=itinerary,
            created_at=datetime.now()
        )
        
        await plans_collection.insert_one(day_plan.dict(by_alias=True))
        return day_plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Server Execution ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)