#========================
#SQA_squad-SQA2025-AUBURN
#keanna Tennyson
# fuzz.py
#created April 15, 2025
# Basic fuzzing script to show any random, or unexpected functions
# to report any crashes or errors in the codebase.
# I also updated the code slightly because of the Path
#========================
#imported subprocess to run the main.py file
import subprocess

#importing from these 5 functions to fuzz
from parser import loadMultiYAML
from scanner import runScanner, getYAMLFiles
from main import main
from graphtaint import mineSecretGraph
from pathlib import Path
from myLogger import giveMeLoggingObject

# I have updated my code to have logging statesments connected to myLogger
# logging config for fuzz.py
logger = giveMeLoggingObject()

# this function creates a static yaml file for testing
def create_static_yaml(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    
# this function fuzzes the loadMultiYAML function
def fuzz_load_multi_yaml():
    logger.info("Running static scanner test using the loadMultiYAML function")
    yaml_path = Path("temp_files/static.yaml")
    yaml_content = """---
name: prod-cache
value: redis://localhost
---
id: 001
description: Configuration for Redis
"""
    create_static_yaml(yaml_path, yaml_content)
    loadMultiYAML(str(yaml_path))
    yaml_path.unlink()

# this function runs a scan with random configs for fuzzing
def fuzz_run_scanner():
    logger.info("Running static scanner test using the runScanner function")
    test_dir = Path("temp_scan")
    yaml_path = test_dir / "test.yaml"
    yaml_content = """apiVersion: v1
kind: Pod
metadata:
  name: cache-service
spec:
  containers:
    - name: redis-container
      image: redis:latest
"""
    create_static_yaml(yaml_path, yaml_content)

    _, sarif_output = runScanner(str(test_dir))
    Path("/results/slikube_results.csv").write_text(sarif_output)

#this function fuzzes the main inputs of the program
def fuzz_main():
    logger.info("Running static scanner test using the Main function")
    result = subprocess.run(
        ["python", "main.py", "/home/TEST_ARTIFACTS"],
        capture_output=True,
        text=True
    )
    logger.info(result.stdout)
    
# this function fuzzes the mine_secret_graph function
def fuzz_mine_secret_graph():
    logger.info("Running static scanner test using the mineSecretGraph function")
    fake_path = "/home/TEST_ARTIFACTS/fake.yaml"
    static_yaml_dict = {
        "kind": "Secret",
        "metadata": {"name": "example-secret"},
        "data": {"username": "admin", "password": "secret123"}
    }
    static_secret_dict = {
        "username": [["admin"]],
        "password": [["secret123"]]
    }
    mineSecretGraph(fake_path, static_yaml_dict, static_secret_dict)

# this function fuzzes the getYAMLFiles function in scanner
def fuzz_get_yaml_files():
    logger.info("Running static scanner test using the getyamlfiles function")
    test_dir = Path("temp_yaml_files")
    files = [
        ("config.yaml", "config: value"),
        ("service.yaml", "kind: Service"),
        ("deployment.yaml", "kind: Deployment")
    ]
    test_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files:
        (test_dir / name).write_text(content)

    getYAMLFiles(str(test_dir))
        
# this function runs the fuzzing process for all functions
if __name__ == "__main__":
    print("==== Starting Fuzzing ====")
    fuzz_load_multi_yaml()
    fuzz_run_scanner()
    fuzz_main()
    fuzz_mine_secret_graph()
    fuzz_get_yaml_files()
    print("==== Fuzzing Complete ====")
