from dataclasses import dataclass
import datetime
import json


def datetime_to_dict(obj):
    """Convert dataclass to dict with datetime serialization"""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return {key: datetime_to_dict(value) for key, value in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [datetime_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: datetime_to_dict(value) for key, value in obj.items()}
    else:
        return obj


@dataclass
class Reactions:
    Total: int
    Sad: int
    Love: int
    Wow: int
    Like: int
    Haha: int
    Angry: int
    Care: int


@dataclass
class Author:
    author_id: int
    fullname: str
    username: str
    profile_url: str
    profile_image_url: str
    profile_image_path: str



@dataclass
class Comment:
    comment_id: int
    url: str
    parent: str
    user_pro_pic: str
    comment_time: datetime
    user_name: str
    user_profile_url: str
    comment_text: str
    author: Author
    reactions: Reactions
    total_views: int
    total_replies: int
    total_reposts: int
    comments_replies_list: list['Comment']

    def to_json(self):
        return json.dumps(datetime_to_dict(self), ensure_ascii=False, indent=4)


@dataclass
class Youtube:
    post_id: int
    source: str
    post_url: str
    posted_at: datetime
    post_text: str
    author: Author
    comments: list[Comment]
    reactions: Reactions
    featured_image: str = ''
    total_comments: int = 0
    total_comments_scraped: int = 0
    percent_comments: float = 0.0
    total_shares: int = 0
    total_views: int = 0
    checksum: str = ''

    def to_json(self):
        return json.dumps(datetime_to_dict(self), ensure_ascii=False, indent=4)