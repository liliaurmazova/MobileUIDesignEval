import os
import sys
import json
import time
from pathlib import Path

from prompts.prompt_constants import PROMPT_DICT, PROMPT_NUMBER

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dataset.dataset_loader import load_first_images, save_images
from model_runner.ollama_models_runner import OllamaModelRunner
from model_runner.llm_as_a_judge_runner import LLMAsJudgeRunner
from config.constants import (
    IMAGES_DIR,
    EVALUATION_RESULTS_PATH,
    MODEL_NAME_1,
    MODEL_NAME_2,
)
from config.ollama_manager import OllamaManager

def ensure_images_exist():
    
    images_dir = Path(IMAGES_DIR)
    if not images_dir.exists():
        print("Images are not found. Loading from dataset...")
        try:
            images = load_first_images()
            saved_count, save_errors = save_images(images, IMAGES_DIR)
            print(f"Loaded and saved {saved_count} images")
            if save_errors > 0:
                print(f"Save errors: {save_errors}")
        except Exception as e:
            print(f"Error loading images: {e}")
            return False
    else:
        existing_images = list(images_dir.glob("*.png"))
        print(f"Found {len(existing_images)} images")
    
    return True

def generate_code_with_ollama():
    
    try:
        runner = OllamaModelRunner()
        
        print(f"Generating code with {MODEL_NAME_1} and {MODEL_NAME_2}...")

        model1_count, model2_count = 0, 0

        if PROMPT_NUMBER == "All":
            # Iterate through each prompt pair
            for prompt_pair in PROMPT_DICT:
                system_prompt = prompt_pair["system_prompt"]
                user_prompt = prompt_pair["user_prompt"]
                results = runner.run_both_models_on_images(system_prompt, user_prompt)

                model1_count += len(results.get("model1", []))
                model2_count += len(results.get("model2", []))

        else:
            # Test on the chosen prompt only
            prompt = PROMPT_DICT[PROMPT_NUMBER]
            system_prompt = prompt["system_prompt"]
            user_prompt = prompt["user_prompt"]

            results = runner.run_both_models_on_images(system_prompt, user_prompt)

            model1_count = len(results.get("model1", []))
            model2_count = len(results.get("model2", []))

        print(f"Model 1 ({MODEL_NAME_1}): {model1_count} files")
        print(f"Model 2 ({MODEL_NAME_2}): {model2_count} files")
        
        return model1_count > 0 and model2_count > 0
        
    except Exception as e:
        print(f"Error generating code: {e}")
        return False

def evaluate_with_llm_judge():
    print("Evaluating code with LLM as a Judge...")
    
    try:
        judge = LLMAsJudgeRunner()
        
        if not judge.api_key:
            print("ANTHROPIC_API_KEY is not installed in the environment")
            return None
        
        evaluation_results = judge.evaluate_all_generated_code()
        
        if evaluation_results:
            total_evaluations = evaluation_results.get("meta", {}).get("total_evaluations", 0)
            print(f"Evaluation completed: {total_evaluations} results")
            return evaluation_results
        else:
            print("Error: Failed to retrieve evaluation results")
            return None
            
    except Exception as e:
        print(f"Error evaluating: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_model_comparison_report(evaluation_results):
    print("Generating model comparison report...")
    
    if not evaluation_results or "detailed_results" not in evaluation_results:
        return {"error": "No data to analyze"}
    
    detailed_results = evaluation_results["detailed_results"]
    
    model1_results = []
    model2_results = []
    
    for result in detailed_results:
        if "error" in result:
            continue
            
        model_name = result.get("meta", {}).get("model_name", "")
        if "Model 1" in model_name or "model1" in model_name.lower():
            model1_results.append(result)
        elif "Model 2" in model_name or "model2" in model_name.lower():
            model2_results.append(result)
    
    def calculate_model_stats(results, model_name):
        if not results:
            return {
                "model_name": model_name,
                "count": 0,
                "average_overall_score": 0,
                "average_criteria_scores": {},
                "successful_evaluations": 0
            }
        
        successful_results = [r for r in results if "error" not in r and r.get("overall_score", 0) > 0]
        
        if not successful_results:
            return {
                "model_name": model_name,
                "count": len(results),
                "average_overall_score": 0,
                "average_criteria_scores": {},
                "successful_evaluations": 0
            }
        
        avg_overall = sum(r.get("overall_score", 0) for r in successful_results) / len(successful_results)
        
        criteria_scores = {}
        criteria_names = ["element_detection", "structural_accuracy", "layout_accuracy", "code_quality", "completeness"]
        
        for criterion in criteria_names:
            scores = []
            for result in successful_results:
                if criterion in result:
                    score = result[criterion].get("score", 0)
                    scores.append(score)
            
            if scores:
                criteria_scores[criterion] = sum(scores) / len(scores)
            else:
                criteria_scores[criterion] = 0
        
        return {
            "model_name": model_name,
            "count": len(results),
            "successful_evaluations": len(successful_results),
            "average_overall_score": round(avg_overall, 2),
            "average_criteria_scores": {k: round(v, 2) for k, v in criteria_scores.items()}
        }
    
    model1_stats = calculate_model_stats(model1_results, MODEL_NAME_1)
    model2_stats = calculate_model_stats(model2_results, MODEL_NAME_2)
    
    model1_score = model1_stats["average_overall_score"]
    model2_score = model2_stats["average_overall_score"]
    
    if model1_score > model2_score:
        winner = MODEL_NAME_1
        winner_score = model1_score
    elif model2_score > model1_score:
        winner = MODEL_NAME_2
        winner_score = model2_score
    else:
        winner = "Tie"
        winner_score = model1_score
    
    recommendations = []
    if abs(model1_score - model2_score) < 0.5:
        recommendations.append("Both models show comparable results")
        recommendations.append("Model selection may depend on specific requirements")
    else:
        recommendations.append(f"Model {winner} shows significantly better results")
        recommendations.append(f"It is recommended to use {winner} for UI code generation")

    model1_strengths = []
    model2_strengths = []
    
    for criterion in model1_stats["average_criteria_scores"]:
        score1 = model1_stats["average_criteria_scores"][criterion]
        score2 = model2_stats["average_criteria_scores"][criterion]
        
        if score1 > score2 + 0.2:
            model1_strengths.append(f"{criterion}: {score1} vs {score2}")
        elif score2 > score1 + 0.2:
            model2_strengths.append(f"{criterion}: {score2} vs {score1}")
    
    comparison_report = {
        "evaluation_summary": {
            "total_images_evaluated": evaluation_results.get("meta", {}).get("total_images", 0),
            "total_evaluations": len(detailed_results),
            "successful_evaluations": model1_stats["successful_evaluations"] + model2_stats["successful_evaluations"],
            "winner": winner,
            "winner_score": winner_score
        },
        "model_comparison": {
            "model1": model1_stats,
            "model2": model2_stats
        },
        "model_strengths": {
            MODEL_NAME_1: model1_strengths,
            MODEL_NAME_2: model2_strengths
        },
        "recommendations": recommendations,
        "raw_evaluation_data": evaluation_results
    }
    
    return comparison_report


def save_comparison_report(report):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_filename = f"model_comparison_report_{timestamp}.json"
    
    results_dir = Path(EVALUATION_RESULTS_PATH)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = results_dir / report_filename
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Report has been saved: {report_path}")
        return str(report_path)
    except Exception as e:
        print(f"Error saving report: {e}")
        return None


def print_summary(report):
    if "error" in report:
        print(f"\nError: {report['error']}")
        return
    
    summary = report.get("evaluation_summary", {})
    model1_data = report.get("model_comparison", {}).get("model1", {})
    model2_data = report.get("model_comparison", {}).get("model2", {})
    
    print("\n" + "=" * 70)
    print("Model comparison summary:")
    print("=" * 70)

    print(f"Total images evaluated: {summary.get('total_images_evaluated', 0)}")
    print(f"Successful evaluations: {summary.get('successful_evaluations', 0)}")

    print(f"\n{MODEL_NAME_1}:")
    print(f"Average score: {model1_data.get('average_overall_score', 0)}/10")
    print(f"Successful evaluations: {model1_data.get('successful_evaluations', 0)}")

    print(f"\n{MODEL_NAME_2}:")
    print(f"Average score: {model2_data.get('average_overall_score', 0)}/10")
    print(f"Successful evaluations: {model2_data.get('successful_evaluations', 0)}")

    winner = summary.get("winner", "Неопределено")
    if winner != "Tie":
        print(f"\nWinner: {winner} ({summary.get('winner_score', 0)}/10)")
    else:
        print(f"\nResult: Tie")
    
    recommendations = report.get("recommendations", [])
    if recommendations:
        print(f"\nRecommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    print("=" * 70)