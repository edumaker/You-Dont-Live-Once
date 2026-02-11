import json
import os
from datetime import datetime

class SimpleKnowledgeBase:
    def __init__(self, db_path: str = "output/qa_database.json"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def add(self, video_file: str, content: dict, qa: dict):
        entry = {
            'id': len(self.data) + 1,
            'video_file': video_file,
            'timestamp': content['timestamp'],
            'screenshot': content.get('roi_path', ''),
            'ai_description': qa['ai_description'],
            'question': qa['question'],
            'your_answer': qa['ai_answer'],
            'tags': qa['tags'],
            'key_point': qa['key_point'],
            'confidence': qa['confidence'],
            'created_at': datetime.now().isoformat(),
        }
        self.data.append(entry)
        self._save()
        return entry['id']
    
    def _save(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_all(self):
        return self.data