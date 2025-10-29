Overall Description

Task: To evaluate and compare models for generating React code from mobile UI screenshots. 

Models to compare: gemma3:4b-it-qat (Google), qwen2:7b (Qwen) //qwen2.5vl:7b given in the task had unfortunately been changed due to insufficient resources on my local machine.

Model parameters (equal for each model under test):
- Maximum number of tokens: 3000
- Temperature: 0.7

Model used as an LLM-as-a-Judge: claude-sonnet-4-5-20250929

Dataset: The first 5 images sampled from the Hugging Face mrtoy/mobile-ui-design dataset.

Focus: Detection of elements and structural accuracy. The other metrics are also used.

Use a PROMPT_NUMBER from prompts\prompt_constants.py to define the prompt to use for models evaluation. "All" means running all the prompts one by one.