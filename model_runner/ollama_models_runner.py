import os
import sys
import base64
import time
from pathlib import Path
from typing import List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import (
    MODEL_NAME_1, MODEL_NAME_2, 
    MAX_TOKENS_1, MAX_TOKENS_2,
    TEMPERATURE_1, TEMPERATURE_2,
    IMAGES_DIR, GENERATED_CODE_DIR, OLLAMA_BASE_URL,
    OLLAMA_REQUEST_TIMEOUT, IMAGE_EXTENSIONS
)
from prompts.prompt_constants import PROMPT_DICT
from utils.image_utils import encode_image_to_base64

import requests


class OllamaModelRunner:
       
    def __init__(self):
        
        self.input_dir = IMAGES_DIR
        self.output_dir = GENERATED_CODE_DIR
        self.ollama_base_url = OLLAMA_BASE_URL
        
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    
    
    def call_ollama_api(self, model_name: str, system_prompt: str, user_prompt: str, 
                       image_base64: str, max_tokens: int = 3000, temperature: float = 0.7) -> str:
        url = f"{self.ollama_base_url}/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "images": [image_base64],
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=OLLAMA_REQUEST_TIMEOUT)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            print(f"Ollama API Error: {e}")
            return f"API error: {str(e)}"
    
    
    
    def process_single_image(self, image_path: str, model_name: str, 
                             system_prompt: str, user_prompt: str,
                           max_tokens: int, temperature: float) -> Tuple[str, str]:
        try:
            print(f"Processing {image_path} with model {model_name}...")
            
            # Кодируем изображение
            image_base64 = encode_image_to_base64(image_path)
            formatted_user_prompt = user_prompt.format(image_path=os.path.basename(image_path))
            
            generated_code = self.call_ollama_api(
                model_name=model_name,
                system_prompt=system_prompt,
                user_prompt=formatted_user_prompt,
                image_base64=image_base64,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if generated_code.startswith("API error:"):
                raise Exception(generated_code)
                
            # Check if the generated code looks valid (contains JSX/React code)
            if not any(keyword in generated_code for keyword in ["return", "<", ">"]):
                raise Exception(f"Generated code doesn't look valid: {generated_code}")
            
            # Generate output filename
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            output_filename = f"{image_name}_model2.jsx" if "2" in model_name else f"{image_name}_model1.jsx"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Clean up the code - add imports and component wrapper if needed
            if "import React" not in generated_code:
                final_code = "import React from 'react';\n\n"
                if "export default" not in generated_code:
                    component_name = "".join(word.capitalize() for word in image_name.split("_"))
                    final_code += f"const {component_name} = () => {{"
                    final_code += generated_code
                    final_code += f"}}\n\nexport default {component_name};"
                else:
                    final_code += generated_code
            else:
                final_code = generated_code
            
            # Save generated code to file
            os.makedirs(self.output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_code)
            
            print(f"\nSuccessfully saved to: {output_path}")
            return final_code, output_path
            
        except Exception as e:
            error_msg = f"Error processing {image_path}: {str(e)}"
            print(error_msg)
            return "", error_msg
    
    
    
    def run_model_on_images(self, system_prompt, user_prompt, model_choice: int = 1) -> List[dict]:
 
        if model_choice == 1:
            model_name = MODEL_NAME_1
            max_tokens = MAX_TOKENS_1
            temperature = TEMPERATURE_1
            model_suffix = "model1"
        elif model_choice == 2:
            model_name = MODEL_NAME_2
            max_tokens = MAX_TOKENS_2
            temperature = TEMPERATURE_2
            model_suffix = "model2"
        else:
            raise ValueError("model_choice should be 1 or 2")

        print(f"Running model {model_name} with parameters:")
        print(f"  Max tokens: {max_tokens}")
        print(f"  Temperature: {temperature}")
        print(f"  Input dir: {self.input_dir}")
        print(f"  Output dir: {self.output_dir}")
        
        image_files = []

        for ext in IMAGE_EXTENSIONS:
            image_files.extend(Path(self.input_dir).glob(f"*{ext}"))
        
        image_files = list(set(image_files))
        image_files.sort() 
        
        if not image_files:
            print(f"No images in {self.input_dir}")
            return []
    
        results = []
        
        for i, image_path in enumerate(image_files, 1):

            generated_code, error_message = self.process_single_image(
                str(image_path), model_name, system_prompt, user_prompt, max_tokens, temperature
            )
            
            image_stem = image_path.stem 
            output_filename = f"{image_stem}_{model_suffix}.jsx"
            output_path = Path(self.output_dir) / output_filename
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    if error_message:
                        f.write(f"// Code generation error:\n// {error_message}\n")
                    else:
                        f.write(generated_code)
                
                
            except Exception as e:
                print(f"Error saving to {output_path}: {e}")
                error_message = f"Save error: {str(e)}"

            result_info = {
                "image_path": str(image_path),
                "image_name": image_path.name,
                "model_name": model_name,
                "output_file": str(output_path),
                "generated_code": generated_code,
                "error_message": error_message,
                "success": not bool(error_message)
            }
            results.append(result_info)
            
            time.sleep(1)
        
        return results


    def run_both_models_on_images(self, system_prompt, user_prompt) -> dict:


        results = {
            "model1": self.run_model_on_images(system_prompt, user_prompt, model_choice=1),
            "model2": self.run_model_on_images(system_prompt, user_prompt, model_choice=2)
        }
        
        return results


