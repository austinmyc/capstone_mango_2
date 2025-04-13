import os
import json
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv
from models import CollectionsParams, EventsParams
from logger import setup_logger
load_dotenv()

logger = setup_logger(name='opensea_client', log_level=logging.INFO)

class OpenSeaClient:
    """Unified client for interacting with the OpenSea API"""
    
    BASE_URL = os.getenv("OPENSEA_BASE_URL")
    
    def __init__(self):
        self.api_key = os.getenv("OPENSEA_API_KEY")
        if not self.api_key:
            logger.error("API key not found in environment variables")
            raise ValueError("OPENSEA_API_KEY environment variable is not set")
        
        self.headers = {
            "accept": "application/json",
            "x-api-key": self.api_key,
            # Add user agent to avoid being blocked
            "User-agent": "Mozilla/5.0 (compatible; OpenSeaClientBot/1.0)"
        }
        logger.debug("OpenSeaClient initialized with API key")
    
    async def get_collections(self, params: CollectionsParams) -> Dict[str, Any]:
        """
        Fetch collections from OpenSea API
        
        Args:
            params: Validated parameters for the collections API
            
        Returns:
            Dict containing collections data
        """
        url = f"{self.BASE_URL}/collections"
        
        request_params = {
            "chain": params.chain,
            "limit": params.limit,
            "include_hidden": str(params.include_hidden).lower(),
        }
        
        if params.cursor:
            request_params["next"] = params.cursor
            
        if params.order_by:
            request_params["order_by"] = params.order_by
        
        logger.info(f"Fetching collections with params: {request_params}")    
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=request_params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed: {response.status} - {error_text}")
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                    
                    data = await response.json()
                    logger.debug(f"Successfully fetched collections. Found {len(data.get('collections', []))} collections")
                    return data
        except Exception as e:
            logger.error(f"Error fetching collections: {str(e)}")
            raise
    
    async def get_all_collections(self, params: CollectionsParams) -> List[Dict[str, Any]]:
        """
        Fetch all collections with pagination
        
        Args:
            params: Validated parameters for the collections API
            
        Returns:
            List of collection objects
        """
        all_collections = []
        next_cursor = params.cursor
        page_count = 0
        
        # Create a copy of params that we can modify
        current_params = CollectionsParams(
            chain=params.chain,
            limit=params.limit,
            include_hidden=params.include_hidden,
            order_by=params.order_by,
            cursor=next_cursor,
            max_pages=params.max_pages
        )
        
        logger.info(f"Starting pagination to fetch all collections (max {params.max_pages} pages)")
        while page_count < params.max_pages:
            page_count += 1
            logger.debug(f"Fetching collections page {page_count}")
            
            data = await self.get_collections(current_params)
            
            collections = data.get("collections", [])
            all_collections.extend(collections)
            
            next_cursor = data.get("next")
            if not next_cursor:
                logger.debug("No more pages to fetch")
                break
                
            # Update the cursor for the next request
            current_params.cursor = next_cursor
                
            # Sleep to avoid rate limiting
            logger.debug("Sleeping to avoid rate limiting")
            await asyncio.sleep(0.5)
        
        logger.info(f"Fetched a total of {len(all_collections)} collections from {page_count} pages")
        return all_collections
    
    async def get_collection_events(self, params: EventsParams) -> Dict[str, Any]:
        """
        Fetch events for a specific collection from OpenSea API
        
        Args:
            params: Validated parameters for the events API
            
        Returns:
            Dict containing events data
        """
        url = f"{self.BASE_URL}/events/collection/{params.collection_slug}"
        
        request_params = {
            "event_type": params.event_type,
            "limit": params.limit
        }
        
        # Convert datetime to timestamp if needed
        if params.after is not None:
            if isinstance(params.after, datetime):
                after = int(params.after.timestamp())
            else:
                after = params.after
            request_params["after"] = after
            
        if params.before is not None:
            if isinstance(params.before, datetime):
                before = int(params.before.timestamp())
            else:
                before = params.before
            request_params["before"] = before
            
        if params.cursor:
            request_params["next"] = params.cursor
        
        logger.info(f"Fetching events for collection '{params.collection_slug}' with params: {request_params}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=request_params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed: {response.status} - {error_text}")
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                    
                    data = await response.json()
                    logger.debug(f"Successfully fetched events. Found {len(data.get('asset_events', []))} events")
                    return data
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
            raise
    
    async def get_all_collection_events(self, params: EventsParams) -> List[Dict[str, Any]]:
        """
        Fetch all events for a collection with pagination
        
        Args:
            params: Validated parameters for the events API
            
        Returns:
            List of event objects
        """
        all_events = []
        next_cursor = params.cursor
        page_count = 0
        
        # Create a copy of params that we can modify
        current_params = EventsParams(
            collection_slug=params.collection_slug,
            event_type=params.event_type,
            after=params.after,
            before=params.before,
            limit=params.limit,
            cursor=next_cursor,
            max_pages=params.max_pages
        )
        
        logger.info(f"Starting pagination to fetch all events for collection '{params.collection_slug}' (max {params.max_pages} pages)")
        while page_count < params.max_pages:
            page_count += 1
            logger.debug(f"Fetching events page {page_count}")
            
            data = await self.get_collection_events(current_params)
            
            events = data.get("asset_events", [])
            all_events.extend(events)
            
            next_cursor = data.get("next")
            if not next_cursor:
                logger.debug("No more pages to fetch")
                break
            
            # Update the cursor for the next request
            current_params.cursor = next_cursor
                
            # Sleep to avoid rate limiting
            logger.debug("Sleeping to avoid rate limiting")
            await asyncio.sleep(0.5)
        
        logger.info(f"Fetched a total of {len(all_events)} events from {page_count} pages")
        return all_events

