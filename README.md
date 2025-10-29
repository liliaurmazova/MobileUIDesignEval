## Overall Description

### Task
To evaluate and compare models for generating React code from mobile UI screenshots. 

### Models to compare
gemma3:4b-it-qat (Google), qwen2:7b (Qwen) //qwen2.5vl:7b given in the task had unfortunately been changed due to insufficient resources on my local machine.

### Model parameters (equal for each model under test):
- Maximum number of tokens: 3000
- Temperature: 0.7

### Model used as an LLM-as-a-Judge
claude-sonnet-4-5-20250929

### Dataset
The first 5 images sampled from the Hugging Face mrtoy/mobile-ui-design dataset.

### Focus
Detection of elements and structural accuracy. The other metrics are also used.

Use a PROMPT_NUMBER from prompts\prompt_constants.py to define the prompt to use for models evaluation. "All" means running all the prompts one by one.

## Project Structure

```
MobileUIDesignEval/
├── config/
│   ├── constants.py           # Global configuration constants
│   └── ollama_manager.py      # Ollama server management
│
├── dataset/
│   ├── __init__.py
│   ├── dataset_loader.py      # Dataset loading and processing
│   ├── mobile_ui_design_images/   # Directory containing UI screenshots
│   └── config/
│       └── constants.py       # Dataset-specific constants
│
├── model_runner/
│   ├── ollama_models_runner.py    # Code generation models execution
│   └── llm_as_a_judge_runner.py   # Evaluation model execution
│
├── prompts/
│   └── prompt_constants.py    # Different prompt variations for testing
│
├── utils/
│   ├── evaluation_analyzer.py # Analysis of evaluation results
│   └── image_utils.py        # Image processing utilities
│
├── output/                    # Generated React components
│   └── *.jsx                 # Output files for each image
│
├── evaluation_results/        # Evaluation results and reports
│   ├── detailed_report.txt   # Detailed evaluation report
│   └── evaluation_results.json    # Structured evaluation data
│
├── main.py                   # Main execution script
└── README.md                 # Project documentation
```

## Key Components

1. **Configuration (`config/`)**
   - Global constants and settings
   - Ollama server management and configuration

2. **Dataset Management (`dataset/`)**
   - Image loading and preprocessing
   - Dataset configuration

3. **Model Execution (`model_runner/`)**
   - Code generation models (Gemma and Qwen)
   - LLM-as-a-Judge evaluation model (Claude)

4. **Prompts (`prompts/`)**
   - Various prompt templates for testing
   - Different styles and approaches for code generation

5. **Utilities (`utils/`)**
   - Evaluation result analysis
   - Image processing tools

6. **Output and Results**
   - Generated React components (`output/`)
   - Evaluation reports and metrics (`evaluation_results/`)

## Running the Project

1. Configure the environment variables (if needed for Claude API)
2. Ensure Ollama is installed and running
3. Set the desired PROMPT_NUMBER in `prompts/prompt_constants.py`
4. Run `main.py` to execute the complete pipeline:
   - Load and process images
   - Generate React components
   - Evaluate the results
   - Generate reports