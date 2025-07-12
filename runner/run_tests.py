# File: runner/run_tests.py

import subprocess
import os
import sys

RESULTS_DIR = "runner/results/logs"
JSON_DIR = "generator/output"
SCRIPTS_DIR = os.path.abspath("scripts")

def get_latest_json_basename():
    """Get the latest .json test file basename from JSON_DIR."""
    if not os.path.exists(JSON_DIR):
        return None

    json_files = [f for f in os.listdir(JSON_DIR) if f.endswith(".json")]
    if not json_files:
        return None

    latest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join(JSON_DIR, f)))
    return os.path.splitext(latest_file)[0]

def run_playwright_tests(base_name):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"[>] Running Playwright tests for: {base_name}")

    log_path = os.path.join(RESULTS_DIR, f"test_{base_name}_log.txt")
    spec_file = f"tests/generated_{base_name}.spec.ts"
    cmd = f"npx playwright test {spec_file} --reporter=html"

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=SCRIPTS_DIR,
    )

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(result.stdout)
        f.write("\n[stderr]\n")
        f.write(result.stderr)

    print(f"[>] Test log saved to: {log_path}")
    print(f"[>] Return Code: {result.returncode}")
    print("[>>>] Tests Passed!" if result.returncode == 0 else "[<<] Some tests failed.")

    return result.returncode == 0, log_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_name = sys.argv[1]
    else:
        base_name = get_latest_json_basename()
        if not base_name:
            print("❌ No .json test cases found in generator/output and no base name provided.")
            sys.exit(1)

    run_playwright_tests(base_name=base_name)
