import os
import json
import re

REQUIRED_FIELDS = {"id", "prompt", "expected", "severity"}

def validate_dataset(data, existing_ids=None):
    if existing_ids is None:
        existing_ids = set()
    
    if not isinstance(data, list):
        raise ValueError("Dataset must be a list of JSON objects")
    
    for item in data:
        for field in REQUIRED_FIELDS:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")
            
        if item["id"] in existing_ids:
            raise ValueError(f"Duplicate id: {item['id']}")
        existing_ids.add(item["id"])
        
        if not item["prompt"]:
            raise ValueError(f"Missing prompt in id: {item['id']}")
            
        if not isinstance(item["expected"], list) or not item["expected"]:
            raise ValueError(f"Missing expected labels in id: {item['id']}")
            
        for pt in item["expected"]:
            if not re.match(r"^PT-\d{3}$", pt) and pt != "benign":
                raise ValueError(f"Invalid PT number: {pt} in id: {item['id']}")

    return True

def load_dataset(file_path, existing_ids=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {str(e)}")
        
    validate_dataset(data, existing_ids)
    return data

def load_directory(dir_path):
    merged = []
    existing_ids = set()
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(root, file)
                data = load_dataset(path, existing_ids)
                merged.extend(data)
    return merged

def merge_datasets(datasets):
    merged = []
    existing_ids = set()
    for dataset in datasets:
        for item in dataset:
            if item["id"] in existing_ids:
                raise ValueError(f"Duplicate id during merge: {item['id']}")
            existing_ids.add(item["id"])
            merged.append(item)
    return merged
