import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

from config import CLASSIFIER_TYPE

_CLASSIFIER = None

def train_classifier(semantic_index: dict):
    """
    Trains the multi-class classifier using the semantic index embeddings.
    """
    global _CLASSIFIER
    
    X = []
    y = []
    
    for technique, data in semantic_index.items():
        # Positive examples
        embeddings = data.get("embeddings", [])
        if len(embeddings) > 0:
            X.extend(embeddings)
            y.extend([technique] * len(embeddings))
            
        # Negative examples -> mapped to 'SAFE'
        negative_embeddings = data.get("negative_embeddings", [])
        if len(negative_embeddings) > 0:
            X.extend(negative_embeddings)
            y.extend(["SAFE"] * len(negative_embeddings))
            
    if not X:
        return
        
    X = np.array(X)
    y = np.array(y)
    
    if CLASSIFIER_TYPE == "linear_svm":
        _CLASSIFIER = SVC(kernel="linear", probability=True, random_state=42)
    elif CLASSIFIER_TYPE == "mlp":
        _CLASSIFIER = MLPClassifier(hidden_layer_sizes=(128,), max_iter=500, random_state=42)
    else:
        _CLASSIFIER = LogisticRegression(max_iter=1000, random_state=42)
        
    _CLASSIFIER.fit(X, y)

def predict(embedding) -> dict:
    """
    Predicts the PT technique for a given embedding.
    Returns predicted PT, probability, top-3 classes, and confidence.
    """
    global _CLASSIFIER
    
    if _CLASSIFIER is None:
        return None
        
    emb_2d = np.array(embedding).reshape(1, -1)
    probs = _CLASSIFIER.predict_proba(emb_2d)[0]
    classes = _CLASSIFIER.classes_
    
    top_indices = np.argsort(probs)[::-1]
    
    top_3_classes = []
    for i in range(min(3, len(top_indices))):
        idx = top_indices[i]
        top_3_classes.append({
            "technique": str(classes[idx]),
            "probability": float(probs[idx])
        })
        
    predicted_pt = top_3_classes[0]["technique"]
    probability = top_3_classes[0]["probability"]
    
    if len(top_3_classes) > 1:
        confidence = probability - top_3_classes[1]["probability"]
    else:
        confidence = probability
        
    return {
        "predicted_pt": predicted_pt,
        "probability": probability,
        "top_3_classes": top_3_classes,
        "confidence": confidence
    }
