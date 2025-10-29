import subprocess
import time
import json

class OllamaManager:
    def __init__(self):
        self.process = None

    def start(self):
        print("Starting Ollama server...")
        if self.process is None:
            try:
                # Check if the server is already running
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    print("Ollama server is already running.")
                    return
            except FileNotFoundError:
                print("Error: 'ollama' command not found. Make sure Ollama is installed and in your PATH.")
                raise

            self.process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("Waiting for Ollama server to be ready...")
            time.sleep(10)  # Wait for the server to start
            print("Ollama server started.")

    def stop(self):
        
        if self.process is not None:
            print("Stopping Ollama server...")
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("Ollama server stopped.")

    def list_models(self):
        
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            models = [line.split()[0] for line in lines[1:]]
            return models
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def pull_model(self, model_name: str):
        
        available_models = self.list_models()
        if model_name in available_models:
            print(f"Model '{model_name}' is already available.")
            return

        print(f"Model '{model_name}' not found. Pulling from Ollama...")
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if process.stdout:
                for line in iter(process.stdout.readline, b''):
                    print(f"> {line.decode().strip()}")
            
            process.wait()
            if process.returncode == 0:
                print(f"Model '{model_name}' pulled successfully.")
            else:
                if process.stderr:
                    stderr = process.stderr.read().decode()
                    print(f"Error pulling model '{model_name}': {stderr}")
        except FileNotFoundError:
            print("Error: 'ollama' command not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def ensure_models_are_pulled(self, model_names: list):
        
        for model_name in model_names:
            self.pull_model(model_name)
