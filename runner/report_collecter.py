# File: runner/report_collector.py

import re
import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime

LOG_DIR = "../runner/results/logs"
FONT_PATH = "../runner/fonts/DejaVuSans.ttf"  # Unicode-safe TTF font

def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def get_latest_log_file():
    log_files = [
        f for f in os.listdir(LOG_DIR)
        if f.endswith("_log.txt")
    ]
    if not log_files:
        return None
    latest_log = sorted(log_files, reverse=True)[0]
    return os.path.join(LOG_DIR, latest_log)

def generate_pdf_summary(log_path=None, base_name=None):
    if not log_path:
        log_path = get_latest_log_file()
    if not log_path or not os.path.exists(log_path):
        print(f"[❌] Log file not found: {log_path}")
        return

    with open(log_path, "r", encoding="utf-8") as f:
        log_content = f.readlines()

    if not base_name:
        base_name = os.path.splitext(os.path.basename(log_path))[0].replace("_log", "")

    pdf_path = os.path.join(LOG_DIR, f"{base_name}_report.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("DejaVu", "", FONT_PATH)
    pdf.set_font("DejaVu", size=10)

    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "📄 Playwright Test Run Report", ln=True, align="r")

    for line in log_content:
        clean_line = remove_ansi_escape_sequences(line.strip())
        try:
            pdf.multi_cell(0, 6, clean_line)
        except Exception:
            pdf.multi_cell(0, 6, "[Unicode decode error]")

    pdf.output(pdf_path)
    print(f"[✅] PDF report generated: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_pdf_summary()
