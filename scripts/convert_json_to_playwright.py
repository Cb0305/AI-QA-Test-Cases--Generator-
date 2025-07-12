import json
import os
import sys

# Use absolute paths to avoid platform-specific path issues
BASE_OUTPUT_DIR = os.path.abspath("scripts/tests")
BASE_INPUT_DIR = os.path.abspath("generator/output")

def convert_to_playwright(test_case):
    title = test_case["title"]
    steps = test_case["steps"]
    expected = test_case.get("expected_result", "")

    test_code = f'  test("{title}", async ({{ page }}) => {{\n'
    for step in steps:
        test_code += f'    // {step}\n'
    if expected:
        test_code += f'    // ✅ Expected: {expected}\n'
    test_code += f'  }});\n'
    return test_code

def main():
    if len(sys.argv) < 2:
        print("❗ Usage: python convert_json_to_playwright.py <base_name>")
        print("   Example: python convert_json_to_playwright.py myvideo_20250706_0830")
        return

    base_name = sys.argv[1]
    input_path = os.path.join(BASE_INPUT_DIR, f"{base_name}.json")
    output_path = os.path.join(BASE_OUTPUT_DIR, f"generated_{base_name}.spec.ts")

    print(f"🔍 Looking for JSON at: {input_path}")

    if not os.path.exists(input_path):
        print(f"[❌] JSON test cases not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"[🧪] Converting {len(test_cases)} test cases to Playwright...")

    test_file = 'import { test, expect } from "@playwright/test";\n\ntest.describe("QA Agent Generated Tests", () => {\n'
    for tc in test_cases:
        test_file += convert_to_playwright(tc)
    test_file += '});\n'

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(test_file)

    print(f"[✅] Playwright test file created at: {output_path}")

if __name__ == "__main__":
    main()
