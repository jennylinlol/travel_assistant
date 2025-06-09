import os
import logging
from typing import Optional
import serpapi
from pydantic import BaseModel, Field
from langchain_core.tools import tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# from pydantic import BaseModel, Field


class HotelsInput(BaseModel):
    q: str = Field(description='Location of the hotel')
    check_in_date: str = Field(description='Check-in date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    check_out_date: str = Field(description='Check-out date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    sort_by: Optional[str] = Field(8, description='Parameter is used for sorting the results. Default is sort by highest rating')
    adults: Optional[int] = Field(1, description='Number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Number of children. Default to 0.')
    rooms: Optional[int] = Field(1, description='Number of rooms. Default to 1.')
    hotel_class: Optional[str] = Field(
        None, description='Parameter defines to include only certain hotel class in the results. for example- 2,3,4')


class HotelsInputSchema(BaseModel):
    params: HotelsInput


@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInput):
    '''
    Find hotels using the Google Hotels engine.

    Returns:
        dict: Hotel search results.
    '''
    # Log hotel tool initiation
    logger.info("🏨 HOTEL TOOL INITIATED")
    logger.info(f"📍 Location: {params.q}")
    logger.info(f"📅 Check-in: {params.check_in_date}")
    logger.info(f"📅 Check-out: {params.check_out_date}")
    logger.info(f"👥 Adults: {params.adults}, Children: {params.children}, Rooms: {params.rooms}")
    
    # Defensive: ensure sort_by is an integer code
    sort_by = params.sort_by
    try:
        sort_by = int(sort_by)
    except (TypeError, ValueError):
        sort_by = 8  # Default to highest rating

    params_dict = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_hotels',
        'hl': 'en',
        'gl': 'us',
        'q': params.q,
        'check_in_date': params.check_in_date,
        'check_out_date': params.check_out_date,
        'currency': 'USD',
        'adults': params.adults,
        'children': params.children,
        'rooms': params.rooms,
        'sort_by': sort_by,
        'hotel_class': params.hotel_class
    }

    logger.info(f"🔍 Searching hotels with parameters: {params_dict}")
    
    try:
        search = serpapi.search(params_dict)
        results = search.data
        
        if 'properties' in results:
            hotel_count = len(results['properties'][:5])
            logger.info(f"✅ Found {hotel_count} hotels")
            return results['properties'][:5]
        else:
            logger.warning("⚠️ No hotel properties found in results")
            return []
            
    except Exception as e:
        logger.error(f"❌ Hotel search failed: {str(e)}")
        raise e
