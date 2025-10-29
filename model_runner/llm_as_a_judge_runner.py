import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import anthropic

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.image_utils import encode_image_to_base64, get_image_mime_type
from prompts.prompt_constants import JUDGE_SYSTEM_PROMPT, JUDGE_USER_PROMPT

from config.constants import (
    LLM_AS_JUDGE_MODEL_NAME,
    LLM_AS_JUDGE_MODEL_MAX_TOKENS,
    LLM_AS_JUDGE_MODEL_TEMPERATURE,
    ANTHROPIC_API_KEY,
    IMAGES_DIR,
    GENERATED_CODE_DIR,
    EVALUATION_RESULTS_PATH,
    IMAGE_EXTENSIONS
)


class LLMAsJudgeRunner:
    def __init__(self, images_dir: Optional[str] = None, code_dir: Optional[str] = None):
   
        self.images_dir = images_dir or IMAGES_DIR
        self.code_dir = code_dir or GENERATED_CODE_DIR
        self.api_key = ANTHROPIC_API_KEY
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        self.evaluation_dir = Path(EVALUATION_RESULTS_PATH)
        self.evaluation_dir.mkdir(exist_ok=True)
    

    
    def read_generated_code(self, code_file_path: str) -> str:
        try:
            with open(code_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading code file: {str(e)}"
    
    
    
    def call_claude_api(self, image_base64: str, generated_code: str, 
                       image_name: str, model_name: str) -> Dict[str, Any]:
          

        try:
            mime_type = get_image_mime_type(image_name)
            
            # Format the user prompt with the generated code
            formatted_prompt = JUDGE_USER_PROMPT.format(
                generated_code=generated_code, 
                model_name=model_name,
                image_name=image_name
            )
            
            messages_data = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text", 
                            "text": formatted_prompt
                        }
                    ]
                }
            ]
            
            message = self.client.messages.create(
                model=LLM_AS_JUDGE_MODEL_NAME,
                max_tokens=LLM_AS_JUDGE_MODEL_MAX_TOKENS,
                temperature=LLM_AS_JUDGE_MODEL_TEMPERATURE,
                system=JUDGE_SYSTEM_PROMPT,
                messages=messages_data  # type: ignore
            )
            
            response_text = ""
            for content_block in message.content:
                try:
                    response_text += content_block.text  # type: ignore
                except AttributeError:
                    response_text += str(content_block)
            
            try:
                # Attempt to parse the entire response as JSON
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If parsing fails, try to extract JSON from markdown
                try:
                    json_match = re.search(r"```json\n({.*?})\n```", response_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    
                    # Fallback to finding the first and last curly brace
                    first_brace = response_text.find('{')
                    last_brace = response_text.rfind('}')
                    if first_brace != -1 and last_brace != -1:
                        json_str = response_text[first_brace:last_brace+1]
                        return json.loads(json_str)

                    raise json.JSONDecodeError("No JSON object found", response_text, 0)

                except json.JSONDecodeError:
                    return {
                        "error": "Failed to parse JSON response",
                        "raw_response": response_text,
                        "overall_score": 0
                    }
        except Exception as e:
            print(f"API call failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": f"API call failed: {str(e)}",
                "overall_score": 0
            }
    
    
    
    def evaluate_single_code(self, image_path: str, code_file_path: str) -> Dict[str, Any]:
 
        try:
            print(f"Evaluating: {os.path.basename(code_file_path)} for {os.path.basename(image_path)}")
            
            image_base64 = encode_image_to_base64(image_path)
            generated_code = self.read_generated_code(code_file_path)
            
            code_filename = os.path.basename(code_file_path)
            if "_model1" in code_filename:
                model_name = "Model 1"
            elif "_model2" in code_filename:
                model_name = "Model 2"
            else:
                model_name = "Unknown Model"
            
            evaluation = self.call_claude_api(
                image_base64=image_base64,
                generated_code=generated_code,
                image_name=os.path.basename(image_path),
                model_name=model_name
            )
            
            evaluation["meta"] = {
                "image_path": image_path,
                "code_file_path": code_file_path,
                "image_name": os.path.basename(image_path),
                "code_filename": code_filename,
                "model_name": model_name
            }
            
            return evaluation
            
        except Exception as e:
            return {
                "error": f"Evaluation failed: {str(e)}",
                "overall_score": 0,
                "meta": {
                    "image_path": image_path,
                    "code_file_path": code_file_path,
                    "error": str(e)
                }
            }
    
    
    
    def find_code_files_for_image(self, image_name: str) -> List[str]:
        image_stem = Path(image_name).stem  # "mobile_ui_001"
        code_files = []
        
        for pattern in [f"{image_stem}_model1.jsx", f"{image_stem}_model2.jsx"]:
            code_file_path = Path(self.code_dir) / pattern
            if code_file_path.exists():
                code_files.append(str(code_file_path))
        
        return code_files
    
    
    
    def evaluate_all_generated_code(self) -> Dict[str, Any]:

        print(f"Images directory: {self.images_dir}")
        print(f"Code directory: {self.code_dir}")
        print(f"Using model: {LLM_AS_JUDGE_MODEL_NAME}")

        image_files = []
        
        for ext in IMAGE_EXTENSIONS:
            image_files.extend(Path(self.images_dir).glob(f"*{ext}"))
            image_files.extend(Path(self.images_dir).glob(f"*{ext.upper()}"))
        
        image_files = sorted(list(set(image_files)))
        
        if not image_files:
            print(f"No images found in {self.images_dir}")
            return {"error": "No images found", "results": []}

        print(f"Found {len(image_files)} images for evaluation")

        all_evaluations = []
        
        for i, image_path in enumerate(image_files, 1):
            
            code_files = self.find_code_files_for_image(image_path.name)
            
            if not code_files:
                print(f"No code files found for {image_path.name}")
                continue
            
            print(f"{len(code_files)} files of code")
            
            for code_file in code_files:
                evaluation = self.evaluate_single_code(str(image_path), code_file)
                all_evaluations.append(evaluation)
                
                if "error" not in evaluation:
                    score = evaluation.get("overall_score", 0)
                    model = evaluation.get("meta", {}).get("model_name", "Unknown")
                    print(f"{model}: {score}/10")
                else:
                    print(f"{evaluation['error']}")
        
        results = {
            "evaluation_summary": self._generate_summary(all_evaluations),
            "detailed_results": all_evaluations,
            "meta": {
                "total_images": len(image_files),
                "total_evaluations": len(all_evaluations),
                "model_used": LLM_AS_JUDGE_MODEL_NAME,
                "images_dir": self.images_dir,
                "code_dir": self.code_dir
            }
        }
        
        results_file = self.evaluation_dir / "evaluation_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results are saved to {results_file}")
        return results
    
    
    
    def _generate_summary(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not evaluations:
            return {"error": "No evaluations to summarize"}
        
        successful_evals = [e for e in evaluations if "error" not in e]
        
        if not successful_evals:
            return {"error": "No successful evaluations"}
        
        model1_evals = [e for e in successful_evals if e.get("meta", {}).get("model_name") == "Model 1"]
        model2_evals = [e for e in successful_evals if e.get("meta", {}).get("model_name") == "Model 2"]
        
        def calc_avg_scores(evals):
            if not evals:
                return {}
            
            avg_overall = sum(e.get("overall_score", 0) for e in evals) / len(evals)
            
            criteria_scores = {}
            for criterion in ["element_detection", "structural_accuracy", "layout_accuracy", "code_quality", "completeness"]:
                scores = [e.get(criterion, {}).get("score", 0) for e in evals]
                criteria_scores[criterion] = sum(scores) / len(scores) if scores else 0
            
            return {
                "average_overall_score": round(avg_overall, 2),
                "average_criteria_scores": {k: round(v, 2) for k, v in criteria_scores.items()},
                "count": len(evals)
            }
        
        return {
            "total_evaluations": len(evaluations),
            "successful_evaluations": len(successful_evals),
            "failed_evaluations": len(evaluations) - len(successful_evals),
            "model1_summary": calc_avg_scores(model1_evals),
            "model2_summary": calc_avg_scores(model2_evals),
            "overall_summary": calc_avg_scores(successful_evals)
        }
    
    
    
    def compare_models(self) -> Dict[str, Any]:

        results = self.evaluate_all_generated_code()
        summary = results.get("evaluation_summary", {})
        
        model1_summary = summary.get("model1_summary", {})
        model2_summary = summary.get("model2_summary", {})
        
        if not model1_summary or not model2_summary:
            return {"error": "Insufficient data for model comparison"}
        
        comparison = {
            "model1_avg_score": model1_summary.get("average_overall_score", 0),
            "model2_avg_score": model2_summary.get("average_overall_score", 0),
            "winner": None,
            "score_difference": 0,
            "detailed_comparison": {}
        }
        
        score1 = comparison["model1_avg_score"]
        score2 = comparison["model2_avg_score"]
        
        if score1 > score2:
            comparison["winner"] = "Model 1"
            comparison["score_difference"] = round(score1 - score2, 2)
        elif score2 > score1:
            comparison["winner"] = "Model 2"
            comparison["score_difference"] = round(score2 - score1, 2)
        else:
            comparison["winner"] = "Tie"
            comparison["score_difference"] = 0
        
        criteria = ["element_detection", "structural_accuracy", "layout_accuracy", "code_quality", "completeness"]
        for criterion in criteria:
            model1_score = model1_summary.get("average_criteria_scores", {}).get(criterion, 0)
            model2_score = model2_summary.get("average_criteria_scores", {}).get(criterion, 0)
            
            comparison["detailed_comparison"][criterion] = {
                "model1_score": model1_score,
                "model2_score": model2_score,
                "difference": round(model1_score - model2_score, 2),
                "winner": "Model 1" if model1_score > model2_score else ("Model 2" if model2_score > model1_score else "Tie")
            }
        
        return comparison


def judge_model_performance():
    try:
        judge = LLMAsJudgeRunner()
        
        results = judge.evaluate_all_generated_code()
        
        summary = results.get("evaluation_summary", {})
        
        if "error" not in summary:
            print(f"Total: {summary.get('successful_evaluations', 0)}")
            
            model1 = summary.get("model1_summary", {})
            model2 = summary.get("model2_summary", {})
            
            if model1:
                print(f"Model 1 average score: {model1.get('average_overall_score', 0)}/10")
            if model2:
                print(f"Model 2 average score: {model2.get('average_overall_score', 0)}/10")

        print("\nStarting model comparison...")
        comparison = judge.compare_models()
        
        if "error" not in comparison:
            print(f"Winner: {comparison.get('winner', 'Unknown')}")
            print(f"Score difference: {comparison.get('score_difference', 0)}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False



