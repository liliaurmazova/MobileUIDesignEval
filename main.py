import os
import sys
import time
from pathlib import Path

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config.constants import (
    MODEL_NAME_1,
    MODEL_NAME_2,
)
from config.ollama_manager import OllamaManager
from utils.evaluation_helper import (
    ensure_images_exist,
    generate_code_with_ollama,
    evaluate_with_llm_judge,
    generate_model_comparison_report,
    save_comparison_report,
    print_summary
)


def main():
    
    ollama_manager = OllamaManager()
    try:
        # Start Ollama server and ensure models are pulled
        ollama_manager.start()
        ollama_manager.ensure_models_are_pulled([MODEL_NAME_1, MODEL_NAME_2])
        
        start_time = time.time()
        
        # Ensure images exist
        if not ensure_images_exist():
            return

        # Generate code with Ollama
        ollama_results = generate_code_with_ollama()
        if not ollama_results:
            return

        # Evaluate with LLM as a Judge
        evaluation_results = evaluate_with_llm_judge()
        if not evaluation_results:
            return

        # Generate and save the comparison report
        comparison_report = generate_model_comparison_report(evaluation_results)
        report_path = save_comparison_report(comparison_report)
        
        # Final summary
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 70)
        print("Pipeline completed successfully!")
        print("=" * 70)
        print(f"Elapsed time: {elapsed_time:.1f} seconds")
        print(f"Report saved: {report_path}")

        print_summary(comparison_report)
        
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
    except Exception as e:
        print(f"\nCritical pipeline error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ollama_manager.stop()

if __name__ == "__main__":
    main()