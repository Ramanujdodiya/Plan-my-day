import React, { useState, useEffect } from 'react';
import './App.css';

const PlanMyDay = () => {
  const [currentStep, setCurrentStep] = useState('location');
  const [planData, setPlanData] = useState({
    location: { lat: null, lng: null, address: '' },
    budget: 100,
    interests: [],
    duration: 'full-day',
    groupSize: 1
  });
  const [dayPlan, setDayPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [weather, setWeather] = useState(null);

<<<<<<< HEAD
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
=======
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
>>>>>>> 238f04647866703c6854f65090c55c3741b5148b

  const interestOptions = [
    'Food & Dining', 'Museums & Culture', 'Outdoor Activities', 'Shopping',
    'Entertainment', 'History', 'Art', 'Music', 'Sports', 'Nature',
    'Architecture', 'Photography', 'Local Experiences'
  ];

  // Get user's location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          
          // Reverse geocode to get address
          try {
            const response = await fetch(
              `https://api.openweathermap.org/geo/1.0/reverse?lat=${lat}&lon=${lng}&limit=1&appid=b6b0b1e2a307b8626098a982fc28bb6b`
            );
            const data = await response.json();
            const address = data[0] ? `${data[0].name}, ${data[0].country}` : 'Current Location';
            
            setPlanData(prev => ({
              ...prev,
              location: { lat, lng, address }
            }));
          } catch (err) {
            setPlanData(prev => ({
              ...prev,
              location: { lat, lng, address: 'Current Location' }
            }));
          }
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  }, []);

  const handleLocationSearch = async (address) => {
    try {
      const response = await fetch(
        `https://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(address)}&limit=1&appid=b6b0b1e2a307b8626098a982fc28bb6b`
      );
      const data = await response.json();
      
      if (data.length > 0) {
        const location = data[0];
        setPlanData(prev => ({
          ...prev,
          location: {
            lat: location.lat,
            lng: location.lon,
            address: `${location.name}, ${location.country}`
          }
        }));
      } else {
        setError('Location not found. Please try a different search.');
      }
    } catch (err) {
      setError('Failed to search location. Please try again.');
    }
  };

  const generatePlan = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(planData)
      });

      if (!response.ok) {
        throw new Error('Failed to generate plan');
      }

      const plan = await response.json();
      setDayPlan(plan);
      setCurrentStep('results');
    } catch (err) {
      setError('Failed to generate day plan. Please try again.');
      console.error('Error generating plan:', err);
    } finally {
      setLoading(false);
    }
  };

  const LocationStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Where are you planning your day?</h2>
        <p className="text-gray-600">We'll use this to find the best local venues and activities</p>
      </div>
      
      <div className="max-w-md mx-auto">
        <div className="flex space-x-2">
          <input
            type="text"
            placeholder="Enter city or address"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleLocationSearch(e.target.value);
              }
            }}
          />
          <button
            onClick={() => {
              const input = document.querySelector('input[placeholder="Enter city or address"]');
              handleLocationSearch(input.value);
            }}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </div>
        
        {planData.location.address && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800">📍 {planData.location.address}</p>
          </div>
        )}
        
        <button
          onClick={() => setCurrentStep('preferences')}
          disabled={!planData.location.lat}
          className="w-full mt-6 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Continue
        </button>
      </div>
    </div>
  );

  const PreferencesStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Tell us your preferences</h2>
        <p className="text-gray-600">We'll create a personalized day plan just for you</p>
      </div>
      
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Budget */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Budget: ${planData.budget}
          </label>
          <input
            type="range"
            min="50"
            max="500"
            value={planData.budget}
            onChange={(e) => setPlanData(prev => ({ ...prev, budget: parseInt(e.target.value) }))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-sm text-gray-500 mt-1">
            <span>$50</span>
            <span>$500</span>
          </div>
        </div>

        {/* Duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Duration</label>
          <div className="grid grid-cols-2 gap-3">
            {['half-day', 'full-day'].map(duration => (
              <button
                key={duration}
                onClick={() => setPlanData(prev => ({ ...prev, duration }))}
                className={`p-3 rounded-lg border-2 transition-colors ${
                  planData.duration === duration
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                {duration === 'half-day' ? '4-6 hours' : '8-12 hours'}
              </button>
            ))}
          </div>
        </div>

        {/* Group Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Group Size: {planData.groupSize} {planData.groupSize === 1 ? 'person' : 'people'}
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={planData.groupSize}
            onChange={(e) => setPlanData(prev => ({ ...prev, groupSize: parseInt(e.target.value) }))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Interests */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            What are you interested in? (Select multiple)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {interestOptions.map(interest => (
              <button
                key={interest}
                onClick={() => {
                  setPlanData(prev => ({
                    ...prev,
                    interests: prev.interests.includes(interest)
                      ? prev.interests.filter(i => i !== interest)
                      : [...prev.interests, interest]
                  }));
                }}
                className={`p-2 text-sm rounded-lg border transition-colors ${
                  planData.interests.includes(interest)
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                {interest}
              </button>
            ))}
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={() => setCurrentStep('location')}
            className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back
          </button>
          <button
            onClick={generatePlan}
            disabled={loading || planData.interests.length === 0}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Creating Your Plan...' : 'Generate Day Plan'}
          </button>
        </div>
      </div>
    </div>
  );

  const ResultsStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Your Perfect Day Plan</h2>
        <p className="text-gray-600">AI-generated itinerary for {planData.location.address}</p>
      </div>

      {dayPlan && (
        <div className="max-w-4xl mx-auto">
          {/* Weather & Budget Summary */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">🌤️ Weather Today</h3>
              <p className="text-blue-800">
                {Math.round(dayPlan.weather.temperature)}°C - {dayPlan.weather.description}
              </p>
              <p className="text-sm text-blue-600">Feels like {Math.round(dayPlan.weather.feels_like)}°C</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">💰 Budget</h3>
              <p className="text-green-800">
                Estimated: ${dayPlan.estimated_cost} / ${dayPlan.total_budget}
              </p>
              <div className="w-full bg-green-200 rounded-full h-2 mt-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{width: `${Math.min((dayPlan.estimated_cost / dayPlan.total_budget) * 100, 100)}%`}}
                ></div>
              </div>
            </div>
          </div>

          {/* Itinerary */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-gray-900">Your Itinerary</h3>
            {dayPlan.itinerary.map((item, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{item.venue.name}</h4>
                    <p className="text-gray-600">{item.venue.category} • {item.venue.price_range}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-blue-600">{item.start_time} - {item.end_time}</p>
                    <p className="text-sm text-gray-500">⭐ {item.venue.rating}</p>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-3">{item.venue.description}</p>
                
                {item.venue.popular_items.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-600 mb-1">Popular items:</p>
                    <div className="flex flex-wrap gap-2">
                      {item.venue.popular_items.map((item_name, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          {item_name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {item.notes && (
                  <p className="text-sm text-blue-600 bg-blue-50 p-2 rounded">{item.notes}</p>
                )}
                
                {item.venue.booking_url && (
                  <a
                    href={item.venue.booking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-3 px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                  >
                    Book Now
                  </a>
                )}
              </div>
            ))}
          </div>

          <div className="flex space-x-3 mt-8">
            <button
              onClick={() => {
                setCurrentStep('preferences');
                setDayPlan(null);
              }}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Create New Plan
            </button>
            <button
              onClick={() => {
                const planText = `My Day Plan for ${dayPlan.location.address}\n\n${dayPlan.itinerary.map(item => 
                  `${item.start_time}-${item.end_time}: ${item.venue.name}\n${item.venue.description}`
                ).join('\n\n')}`;
                navigator.clipboard.writeText(planText);
                alert('Plan copied to clipboard!');
              }}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Share Plan
            </button>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🗓️ PlanMyDay
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered day planning that creates perfect itineraries just for you
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="max-w-md mx-auto mb-8">
          <div className="flex items-center">
            {['location', 'preferences', 'results'].map((step, index) => (
              <React.Fragment key={step}>
                <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  currentStep === step
                    ? 'bg-blue-600 text-white'
                    : index < ['location', 'preferences', 'results'].indexOf(currentStep)
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {index < ['location', 'preferences', 'results'].indexOf(currentStep) ? '✓' : index + 1}
                </div>
                {index < 2 && (
                  <div className={`flex-1 h-1 ${
                    index < ['location', 'preferences', 'results'].indexOf(currentStep)
                      ? 'bg-green-600'
                      : 'bg-gray-300'
                  }`} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-md mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">⚠️ {error}</p>
            <button 
              onClick={() => setError('')}
              className="text-sm text-red-600 underline mt-1"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Step Content */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {currentStep === 'location' && <LocationStep />}
          {currentStep === 'preferences' && <PreferencesStep />}
          {currentStep === 'results' && <ResultsStep />}
        </div>
      </div>
    </div>
  );
};

export default PlanMyDay;