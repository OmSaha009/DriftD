"""Configuration management for Driftd"""

from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path

@dataclass(frozen=True)
class Config:

    poll_interval: float = 2.0
    path_db: Path = Path("data/usage.py")

    category_map: Dict[str, str] = field(default_factory=lambda: {
        # Social
        "youtube": "social",
        "instagram": "social",
        "twitter": "social",
        "reddit": "social",
        
        # Gaming  
        "valorant": "gaming",
        "steam": "gaming",
        "epic games": "gaming",
        
        # Study
        "notion": "study",
        "obsidian": "study",
        "pdf": "study",
        "pw.live": "study",
        
        # Music
        "spotify": "music",
        "apple music": "music",
    })

    def get_category(self, app_name: str, window_title: str) -> str:
        text = f"{app_name} {window_title}".lower()

        for application, category in self.category_map.items():
            if application in text:
                return category
        return "other"