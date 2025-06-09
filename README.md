# AI Travel Assistant

This project is an AI-powered travel planner that helps users generate personalized travel itineraries, including flights, hotels, attractions, weather forecasts, packing tips, and more. The main application is built with Streamlit for an interactive web experience.

## Features

- **Personalized Itinerary**: Generates a daily travel plan based on your preferences, energy level, and budget.
- **Flight & Hotel Search**: Finds the best flight and hotel options for your trip.
- **Weather Forecast**: Integrates real-time weather data for your destination and travel dates.
- **Packing Tips & Checklist**: Suggests what to pack based on the weather and your activities.
- **Attractions & Restaurants**: Recommends local attractions and dining options.

## Project Structure

```
app/travel_assistant/
│
├── agents/
│   ├── agent.py           # Main agent logic for the Streamlit app
│   ├── agent_react.py     # Minimal demo of LangGraph ReAct agent (see below)
│   └── tools/             # Tool definitions (weather, flights, hotels)
│
├── travel_assistant.py    # Main Streamlit app entry point
├── requirements.txt       # Python dependencies
└── __init__.py
```

## Setup & Installation

1. **Clone the repository** and navigate to the `app/travel_assistant` directory.

2. **Install dependencies** (preferably in a virtual environment):

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   - `OPENAI_API_KEY`: Your OpenAI API key (for LLM).
   - `WEATHER_API_KEY`: Your WeatherAPI.com key (for weather forecasts).
   - `SERPAPI_API_KEY`: Your SerpAPI key (for flights and hotels).

   You can use a `.env` file or set these in your shell.

4. **Run the Streamlit app**:

   ```bash
   streamlit run travel_assistant.py
   ```

5. **Open your browser** to the provided local URL to use the app.

## Usage

- Enter your departure and destination airports, travel dates, preferences, energy level, and (optionally) your budget.
- Click **Get Travel Plan** to generate a detailed itinerary.
- The app will display your plan, including weather, flights, hotels, and more.

## About `agent_react.py`

The file `agents/agent_react.py` is **not part of the main Streamlit app**.  
It is a **standalone demo script** that shows how to use the [LangGraph ReAct agent framework](https://github.com/langchain-ai/langgraph) with a simple weather tool.  
You can run it directly to see how a minimal agent works:

```bash
python agents/agent_react.py
```

This is useful for learning and experimentation, but is not required for running the main travel assistant app.

## Dependencies

- `streamlit`
- `openai`
- `langgraph`
- `requests`
- `serpapi`

(See `requirements.txt` for details.)

