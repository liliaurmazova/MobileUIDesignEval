import os

DATASET_NAME = "mrtoy/mobile-ui-design"
SPLIT_NAME = "train" 
IMAGES_DIR = "./dataset/mobile_ui_design_images"
GENERATED_CODE_DIR = "./output"
NUM_SAMPLES = 5

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_REQUEST_TIMEOUT = 600  # Timeout in seconds for Ollama API requests

MODEL_NAME_1 = "gemma3:4b-it-qat"
MAX_TOKENS_1 = 3000
TEMPERATURE_1 = 0.7

MODEL_NAME_2 = "qwen2:7b"
MAX_TOKENS_2 = 3000
TEMPERATURE_2 = 0.7

LLM_AS_JUDGE_MODEL_NAME = "claude-sonnet-4-5-20250929"
LLM_AS_JUDGE_MODEL_MAX_TOKENS = 3000
LLM_AS_JUDGE_MODEL_TEMPERATURE = 0.7
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

DATASET_PATH = "dataset\\mobile_ui_design_images"
GENERATED_OUTPUT_PATH = "output"
EVALUATION_RESULTS_PATH = "./evaluation_results"
EVALUATION_REPORT_PATH = "./evaluation_results/detailed_report.txt"
EVALUATION_RESULTS_JSON_PATH = "./evaluation_results/evaluation_results.json"

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.PNG', '.JPG', '.JPEG', '.GIF', '.BMP']
