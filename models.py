from pydantic import BaseModel, HttpUrl, DirectoryPath
from typing import Optional, List
from datetime import datetime


class TopicSummary(BaseModel):
    id: int
    title: str
    created_at: datetime
    bumped_at: datetime
    
    class Config:
        extra = "ignore"

class TopicList(BaseModel):
    topics: List[TopicSummary]
    
    class Config:
        extra = "ignore"

class TagResponse(BaseModel):
    topic_list: TopicList
    
    class Config:
        extra = "ignore"

class Image(BaseModel):
    url: HttpUrl
    hash: str
    filename: Optional[str] = None
    downloaded_at: Optional[datetime] = None
