from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Publisher:
    id: str
    name: str
    type: str
    url: str

@dataclass
class FeedSpec:
    publisher: Publisher
    title: str
    url: str # Moved before categories
    categories: List[str] = field(default_factory=list)
    # Optional: Add an id if feed_specs.csv has a unique ID column for specs themselves
    # spec_id: Optional[str] = None
