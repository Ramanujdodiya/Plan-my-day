import asyncio
import motor.motor_asyncio
from pymongo import ASCENDING

# --- Our Custom Venue Data ---
# You can edit, add, or remove venues from this list.
OUR_VENUES = [
    {
        "name": "Tech Cafe 2049",
        "category": "restaurant",
        "location": {"lat": 12.9716, "lng": 77.5946},
        "price_range": "$$",
        "rating": 4.7,
        "popular_dishes": ["Quantum Quiche", "Neural-Net Nachos"],
        "booking_url": "https://example.com/book/techcafe"
    },
    {
        "name": "The Green Leaf Bistro",
        "category": "restaurant",
        "location": {"lat": 12.9345, "lng": 77.6244},
        "price_range": "$$$",
        "rating": 4.9,
        "popular_dishes": ["Avocado Toast", "Kale Smoothie", "Vegan Burger"],
        "booking_url": "https://example.com/book/greenleaf"
    },
    {
        "name": "City Art Gallery",
        "category": "attraction",
        "location": {"lat": 12.9757, "lng": 77.5929},
        "price_range": "$",
        "rating": 4.6,
        "description": "Features modern and contemporary art from local artists.",
    },
    {
        "name": "Innovate Hub",
        "category": "activity",
        "location": {"lat": 12.9279, "lng": 77.6271},
        "price_range": "Free",
        "rating": 4.8,
        "description": "A co-working and event space for tech enthusiasts. Hosts weekly meetups."
    },
    {
        "name": "The Escape Room: Sector 7",
        "category": "activity",
        "location": {"lat": 12.9352, "lng": 77.6169},
        "price_range": "$$$",
        "rating": 4.9,
        "description": "A challenging sci-fi themed escape room adventure.",
        "booking_url": "https://example.com/book/escaperoom7"
    },
    {
        "name": "Rooftop Cinema Club",
        "category": "event",
        "location": {"lat": 12.9592, "lng": 77.6455},
        "price_range": "$$",
        "rating": 4.7,
        "description": "Outdoor movie screenings with classic films and city views.",
        "booking_url": "https://example.com/book/rooftopcinema"
    },
    {
        "name": "Downtown Music Hall",
        "category": "event",
        "location": {"lat": 12.9845, "lng": 77.5995},
        "price_range": "$$$",
        "rating": 4.6,
        "description": "Live music venue featuring indie bands and international artists.",
        "booking_url": "https://example.com/book/downtownmusic"
    }
]

async def populate_database():
    """
    Connects to MongoDB, clears the existing venues collection,
    and inserts our new custom venue data.
    """
    print("Connecting to MongoDB...")
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["planmyday"]
    venues_collection = db["venues"]

    print("Deleting existing venues...")
    await venues_collection.delete_many({})

    print(f"Inserting {len(OUR_VENUES)} new venues...")
    await venues_collection.insert_many(OUR_VENUES)

    # Create a geospatial index for location-based queries
    print("Creating geospatial index on 'location' field...")
    await venues_collection.create_index([("location", "2dsphere")])
    
    print("\nDatabase population complete!")
    print(f"Total venues in collection: {await venues_collection.count_documents({})}")

if __name__ == "__main__":
    asyncio.run(populate_database())