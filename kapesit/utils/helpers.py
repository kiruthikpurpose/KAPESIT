import json
from typing import Any, Dict, List, Optional
import hashlib
import base64
import pickle

def serialize(obj: Any) -> str:
    """Serialize any object to a base64 encoded string."""
    return base64.b64encode(pickle.dumps(obj)).decode('utf-8')

def deserialize(serialized: str) -> Any:
    """Deserialize a base64 encoded string back to object."""
    return pickle.loads(base64.b64decode(serialized.encode('utf-8')))

def generate_hash(data: str) -> str:
    """Generate SHA-256 hash for given data."""
    return hashlib.sha256(data.encode()).hexdigest()

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def to_json(obj: Any) -> str:
    """Convert object to JSON string."""
    return json.dumps(obj, default=lambda x: str(x), indent=2)

def from_json(json_str: str) -> Any:
    """Convert JSON string to object."""
    return json.loads(json_str)
