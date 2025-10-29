
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

from config.constants import EVALUATION_REPORT_PATH, EVALUATION_RESULTS_JSON_PATH

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EvaluationAnalyzer:
 
    def __init__(self, results_path: str = EVALUATION_RESULTS_JSON_PATH):
       
        self.results_path = results_path
        self.results = None
        
    def load_results(self) -> bool:
        
        try:
            with open(self.results_path, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading results: {e}")
            return False
    
    def generate_detailed_report(self) -> str:
       
        if not self.results:
            return "Results not loaded"

        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DETAILED REPORT OF LLM AS A JUDGE")
        report_lines.append("=" * 60)

        meta = self.results.get("meta", {})
        report_lines.append(f"\nGeneral Information:")
        report_lines.append(f"  Total Images: {meta.get('total_images', 'N/A')}")
        report_lines.append(f"  Total Evaluations: {meta.get('total_evaluations', 'N/A')}")
        report_lines.append(f"  Judge Model: {meta.get('model_used', 'N/A')}")

        # Summary statistics
        summary = self.results.get("evaluation_summary", {})
        if summary and "error" not in summary:
            report_lines.append(f"\nSummary Statistics:")
            report_lines.append(f"  Successful Evaluations: {summary.get('successful_evaluations', 0)}")
            report_lines.append(f"  Failed Evaluations: {summary.get('failed_evaluations', 0)}")

            # Model statistics
            for model_key in ["model1_summary", "model2_summary"]:
                model_data = summary.get(model_key, {})
                if model_data:
                    model_name = "Model 1" if model_key == "model1_summary" else "Model 2"
                    report_lines.append(f"\n  {model_name}:")
                    report_lines.append(f"    Average Overall Score: {model_data.get('average_overall_score', 0):.2f}/10")
                    report_lines.append(f"    Number of Evaluations: {model_data.get('count', 0)}")

                    criteria_scores = model_data.get('average_criteria_scores', {})
                    if criteria_scores:
                        report_lines.append(f"    Average Scores by Criterion:")
                        for criterion, score in criteria_scores.items():
                            report_lines.append(f"      {criterion}: {score:.2f}/10")
        
        
        detailed_results = self.results.get("detailed_results", [])
        if detailed_results:
            report_lines.append(f"\n" + "=" * 40)
            report_lines.append("DETAILED RESULTS BY IMAGE")
            report_lines.append("=" * 40)

            
            results_by_image = {}
            for result in detailed_results:
                if "error" not in result:
                    image_name = result.get("meta", {}).get("image_name", "unknown")
                    if image_name not in results_by_image:
                        results_by_image[image_name] = []
                    results_by_image[image_name].append(result)
            
            for image_name, image_results in results_by_image.items():
                report_lines.append(f"\n📱 {image_name}")
                report_lines.append("-" * 40)
                
                for result in image_results:
                    model_name = result.get("meta", {}).get("model_name", "Unknown")
                    overall_score = result.get("overall_score", 0)
                    
                    report_lines.append(f"\n  {model_name}: {overall_score}/10")
                    
                    
                    criteria = ["element_detection", "structural_accuracy", "layout_accuracy", "code_quality", "completeness"]
                    for criterion in criteria:
                        criterion_data = result.get(criterion, {})
                        if criterion_data:
                            score = criterion_data.get("score", 0)
                            explanation = criterion_data.get("explanation", "").strip()
                            
                            report_lines.append(f"    {criterion}: {score}/10")
                            if explanation:
                                report_lines.append(f"      {explanation}")
                    
                    
                    strengths = result.get("strengths", [])
                    if strengths:
                        report_lines.append(f"Strengths: {', '.join(strengths)}")
                    
                    weaknesses = result.get("weaknesses", [])
                    if weaknesses:
                        report_lines.append(f"Weaknesses: {', '.join(weaknesses)}")
                    
                    summary_text = result.get("summary", "").strip()
                    if summary_text:
                        report_lines.append(f"Summary: {summary_text}")
        
        return "\n".join(report_lines)
    
        
    def find_best_and_worst_results(self) -> Dict[str, Any]:
        
        if not self.results:
            return {"error": "Results not loaded"}
        
        detailed_results = self.results.get("detailed_results", [])
        successful_results = [r for r in detailed_results if "error" not in r and "overall_score" in r]
        
        if not successful_results:
            return {"error": "No successful results for analysis"}
        
        # Sort by overall score
        sorted_results = sorted(successful_results, key=lambda x: x.get("overall_score", 0))
        
        worst_results = sorted_results[:3]  # 3 worst
        best_results = sorted_results[-3:][::-1]  # 3 best
        
        return {
            "best_results": [
                {
                    "image_name": r.get("meta", {}).get("image_name", "unknown"),
                    "model_name": r.get("meta", {}).get("model_name", "unknown"),
                    "overall_score": r.get("overall_score", 0),
                    "summary": r.get("summary", "")
                } for r in best_results
            ],
            "worst_results": [
                {
                    "image_name": r.get("meta", {}).get("image_name", "unknown"),
                    "model_name": r.get("meta", {}).get("model_name", "unknown"),
                    "overall_score": r.get("overall_score", 0),
                    "summary": r.get("summary", "")
                } for r in worst_results
            ]
        }
    
    def calculate_pass_at_k_metrics(self, k_values: List[int] = [1, 3, 5]) -> Dict[str, Any]:
        
        if not self.results:
            return {"error": "Results not loaded"}

        detailed_results = self.results.get("detailed_results", [])
        successful_results = [r for r in detailed_results if "error" not in r and "overall_score" in r]
        
        if not successful_results:
            return {"error": "No data for pass@k calculation"}

        # Define threshold values for "passing" the test
        thresholds = [5, 6, 7, 8, 9]  # Different success thresholds

        pass_at_k_results = {}
        
        for threshold in thresholds:
            pass_at_k_results[f"threshold_{threshold}"] = {}

            # Group results by image
            results_by_image = {}
            for result in successful_results:
                image_name = result.get("meta", {}).get("image_name", "unknown")
                if image_name not in results_by_image:
                    results_by_image[image_name] = []
                results_by_image[image_name].append(result.get("overall_score", 0))

            # Compute pass@k for each k
            for k in k_values:
                passed_images = 0
                total_images = len(results_by_image)
                
                for image_name, scores in results_by_image.items():
                    # Take top-k results for this image
                    top_k_scores = sorted(scores, reverse=True)[:k]
                    # Check if there's at least one result above the threshold
                    if any(score >= threshold for score in top_k_scores):
                        passed_images += 1
                
                pass_rate = passed_images / total_images if total_images > 0 else 0
                pass_at_k_results[f"threshold_{threshold}"][f"pass@{k}"] = round(pass_rate, 3)
        
        return {
            "pass_at_k_metrics": pass_at_k_results,
            "total_images": len(results_by_image) if 'results_by_image' in locals() else 0
        }
    
    def save_report(self, output_path: str = EVALUATION_REPORT_PATH):
        
        report = self.generate_detailed_report()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Report saved to {output_path}")


