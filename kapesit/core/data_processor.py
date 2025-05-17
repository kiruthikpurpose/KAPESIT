import numpy as np
from typing import List, Dict, Any, Optional
import json
import pickle
from datetime import datetime
import hashlib

class DataProcessor:
    def __init__(self):
        self.processed_data = {}
        self.cache = {}
        self.processing_times = {}

    def process_numeric_data(self, data: List[float]) -> Dict[str, Any]:
        if not data:
            return {}
            
        return {
            'mean': np.mean(data),
            'median': np.median(data),
            'std_dev': np.std(data),
            'variance': np.var(data),
            'min': np.min(data),
            'max': np.max(data),
            'quartiles': np.percentile(data, [25, 50, 75]),
            'range': np.max(data) - np.min(data)
        }

    def process_text_data(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}
            
        words = text.split()
        return {
            'word_count': len(words),
            'unique_words': len(set(words)),
            'average_word_length': np.mean([len(word) for word in words]),
            'character_count': len(text),
            'uppercase_count': sum(1 for c in text if c.isupper()),
            'lowercase_count': sum(1 for c in text if c.islower()),
            'numeric_count': sum(1 for c in text if c.isdigit()),
            'special_chars': sum(1 for c in text if not c.isalnum())
        }

    def process_time_series(self, timestamps: List[datetime]) -> Dict[str, Any]:
        if not timestamps:
            return {}
            
        timestamps.sort()
        return {
            'start_time': timestamps[0],
            'end_time': timestamps[-1],
            'duration': (timestamps[-1] - timestamps[0]).total_seconds(),
            'time_range': (timestamps[-1] - timestamps[0]),
            'average_interval': np.mean([
                (timestamps[i+1] - timestamps[i]).total_seconds()
                for i in range(len(timestamps)-1)
            ]),
            'max_gap': max([
                (timestamps[i+1] - timestamps[i]).total_seconds()
                for i in range(len(timestamps)-1)
            ])
        }

    def cache_data(self, key: str, data: Any) -> None:
        self.cache[key] = {
            'data': pickle.dumps(data),
            'timestamp': datetime.now(),
            'hash': hashlib.sha256(pickle.dumps(data)).hexdigest()
        }

    def get_cached_data(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
            
        cached = self.cache[key]
        return pickle.loads(cached['data'])

    def process_batch(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for item in data:
            processed = {}
            for key, value in item.items():
                if isinstance(value, (list, tuple)) and all(isinstance(x, (int, float)) for x in value):
                    processed[key] = self.process_numeric_data(value)
                elif isinstance(value, str):
                    processed[key] = self.process_text_data(value)
                elif isinstance(value, (list, tuple)) and all(isinstance(x, datetime) for x in value):
                    processed[key] = self.process_time_series(value)
            results.append(processed)
        return results

    def generate_report(self, data: Dict[str, Any]) -> str:
        report = []
        for key, value in data.items():
            if isinstance(value, dict):
                report.append(f"\n{key.upper()} ANALYSIS:")
                for metric, result in value.items():
                    report.append(f"  {metric}: {result}")
        return '\n'.join(report)

class DataValidator:
    def __init__(self):
        self.validation_rules = {}
        self.validation_errors = {}

    def add_rule(self, field: str, rule: callable, message: str) -> None:
        self.validation_rules[field] = (rule, message)

    def validate(self, data: Dict[str, Any]) -> bool:
        self.validation_errors = {}
        valid = True
        
        for field, (rule, message) in self.validation_rules.items():
            if field in data and not rule(data[field]):
                self.validation_errors[field] = message
                valid = False
        
        return valid

    def validate_batch(self, data_list: List[Dict[str, Any]]) -> List[bool]:
        return [self.validate(item) for item in data_list]

    def get_validation_errors(self) -> Dict[str, str]:
        return self.validation_errors

class DataTransformer:
    def __init__(self):
        self.transformations = {}

    def add_transformation(self, field: str, transformation: callable) -> None:
        self.transformations[field] = transformation

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        transformed = data.copy()
        for field, transformation in self.transformations.items():
            if field in transformed:
                transformed[field] = transformation(transformed[field])
        return transformed

    def transform_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.transform(item) for item in data_list]
