import os
import torch
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
from typing import Optional, Dict

_text_model: Optional[SentenceTransformer] = None
_clip_model: Optional[CLIPModel] = None
_clip_processor: Optional[CLIPProcessor] = None

# In-memory embedding cache keyed by file path or text content
_image_cache: Dict[str, np.ndarray] = {}
_text_cache: Dict[str, np.ndarray] = {}


def get_text_model() -> SentenceTransformer:
    global _text_model
    if _text_model is None:
        print("[TRACE] Loading SentenceTransformer 'all-MiniLM-L6-v2'...")
        _text_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _text_model


def get_clip_model():
    global _clip_model, _clip_processor
    if _clip_model is None or _clip_processor is None:
        model_name = "openai/clip-vit-base-patch32"
        print(f"[TRACE] Loading CLIP model '{model_name}'...")
        try:
            _clip_processor = CLIPProcessor.from_pretrained(model_name)
            _clip_model = CLIPModel.from_pretrained(model_name)
            _clip_model.eval()
        except Exception as e:
            print(f"[TRACE WARNING] Error loading {model_name}: {e}. Retrying with CPU settings...")
            _clip_processor = CLIPProcessor.from_pretrained(model_name)
            _clip_model = CLIPModel.from_pretrained(model_name)
            _clip_model.eval()
    return _clip_processor, _clip_model


def get_text_embedding(text: str) -> np.ndarray:
    """Compute normalized sentence embedding for a given text string."""
    cleaned = (text or "").strip()
    if not cleaned:
        return np.zeros(384, dtype=np.float32)
    if cleaned in _text_cache:
        return _text_cache[cleaned]

    model = get_text_model()
    vec = model.encode(cleaned, normalize_embeddings=True)
    vec = np.asarray(vec, dtype=np.float32)
    _text_cache[cleaned] = vec
    return vec


def get_image_embedding(image_path: str) -> Optional[np.ndarray]:
    """Compute normalized CLIP visual embedding for an image file."""
    if not image_path or not os.path.exists(image_path):
        return None
    
    # Check cache by mtime + path
    stat = os.stat(image_path)
    cache_key = f"{image_path}:{stat.st_mtime}"
    if cache_key in _image_cache:
        return _image_cache[cache_key]

    try:
        processor, model = get_clip_model()
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            if isinstance(outputs, torch.Tensor):
                image_features = outputs
            elif hasattr(outputs, "pooler_output") and outputs.pooler_output is not None:
                image_features = outputs.pooler_output
            elif hasattr(outputs, "last_hidden_state") and outputs.last_hidden_state is not None:
                image_features = outputs.last_hidden_state[:, 0, :]
            else:
                image_features = outputs[0]

            # Normalize vector
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            vec = image_features.cpu().numpy().flatten().astype(np.float32)
            _image_cache[cache_key] = vec
            return vec
    except Exception as ex:
        print(f"[TRACE ERROR] Failed to generate CLIP embedding for {image_path}: {ex}")
        return None


def cosine_similarity(v1: Optional[np.ndarray], v2: Optional[np.ndarray]) -> float:
    """Calculate cosine similarity clamped to [0.0, 1.0]."""
    if v1 is None or v2 is None:
        return 0.0
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    sim = float(np.dot(v1, v2) / (norm1 * norm2))
    # CLIP / MiniLM cosine similarities can be slightly negative or >1 due to float precision
    return max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))
