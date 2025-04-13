from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator

class CollectionsParams(BaseModel):
    """Validation model for collections API parameters"""
    chain: str = Field(default="ethereum", description="Filter by blockchain")
    limit: int = Field(default=50, ge=1, le=100, description="Number of collections to return (max 100)")
    include_hidden: bool = Field(default=False, description="Include hidden collections")
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination")
    order_by: Optional[str] = Field(default=None, description="Sort order (e.g., 'created_date')")
    max_pages: int = Field(default=10, ge=1, description="Maximum number of pages to fetch")
    
    # Optional validation for additional parameters
    @validator("chain")
    def validate_chain(cls, v):
        valid_chains = ["ethereum", "polygon", "klaytn", "solana", "arbitrum", "optimism", "avalanche"]
        if v.lower() not in valid_chains:
            raise ValueError(f"Invalid chain. Must be one of: {', '.join(valid_chains)}")
        return v.lower()

class EventsParams(BaseModel):
    """Validation model for events API parameters"""
    collection_slug: str = Field(..., min_length=1, description="Collection identifier (e.g., 'doodles-official')")
    event_type: List[str] = Field(default=["sale"], description="Types of events to fetch")
    after: Optional[Union[int, datetime]] = Field(default=None, description="Start timestamp")
    before: Optional[Union[int, datetime]] = Field(default=None, description="End timestamp")
    limit: int = Field(default=50, ge=1, le=50, description="Number of events to return (max 50)")
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination")
    max_pages: int = Field(default=10, ge=1, description="Maximum number of pages to fetch")
    
    # Validate event types
    @validator("event_type")
    def validate_event_type(cls, v):
        valid_types = ["sale", "transfer", "mint", "burn", "approve", "bid_entered", "bid_withdrawn", "offer_entered", "offer_withdrawn", "cancel"]
        for event_type in v:
            if event_type not in valid_types:
                raise ValueError(f"Invalid event type: {event_type}. Must be one of: {', '.join(valid_types)}")
        return v 