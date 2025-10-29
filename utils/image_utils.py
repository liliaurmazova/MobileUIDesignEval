import base64
from typing import Optional


def encode_image_to_base64(image_path: str) -> str:
 
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except IOError as e:
        raise IOError(f"Error reading image file {image_path}: {str(e)}")


def get_image_mime_type(image_path: str) -> str:
   
    extension = image_path.lower().split('.')[-1]
    
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp'
    }
    
    return mime_types.get(extension, 'image/png')  # Default to 'image/png' if unknown extension