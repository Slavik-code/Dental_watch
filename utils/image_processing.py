import numpy as np

def normalize_image(img_data):
    """Нормализует массив пикселей в диапазон 0..255 (uint8)."""
    min_val = np.min(img_data)
    max_val = np.max(img_data)
    if max_val == min_val:
        return np.zeros_like(img_data, dtype=np.uint8)
    return ((img_data - min_val) / (max_val - min_val) * 255).astype(np.uint8)