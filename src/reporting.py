import os
import logging
import pandas as pd
from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Fitbit Consolidated Health Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def add_info_box(self, label, status, reason, critical=False):
        color = (255, 230, 230) if critical else (245, 245, 245)
        self.set_fill_color(*color)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, f"Metric: {label}", 'TLR', 1, 'L', 1)
        self.set_font('Arial', 'I', 9)
        self.multi_cell(0, 6, f"Status: {status}\nReason: {reason}", 'BLR', 'L', 1)
        self.ln(3)

def generate_pdf_report(subject_name, config):
    report_dir = os.path.join("reports", subject_name)
    output_pdf = os.path.join(report_dir, f"{subject_name}_Detailed_Report.pdf")
    
    target_metrics = {
        "glucose": "Glucose", "heart_rate": "Heart Rate", 
        "sleep_score": "Sleep Score", "stress_score": "Stress Score",
        "oxygen": "Oxygen Saturation", "activity": "Physical Activity"
    }
    
    pdf = PDFReport()
    pdf.add_page()
    pdf.chapter_title("1. Data Quality Assessment")
    
    valid_keys = []
    if not os.path.exists(report_dir): return
    files = os.listdir(report_dir)

    # CHECK FOR VALID DATA
    for key, label in target_metrics.items():
        csv_file = f"summary_weekly_{key}.csv"
        
        if csv_file in files:
            df = pd.read_csv(os.path.join(report_dir, csv_file)).dropna()
            if len(df) >= 2:
                valid_keys.append(key)
                pdf.add_info_box(label, "Valid", f"Successfully processed {len(df)} weeks.")
            else:
                pdf.add_info_box(label, "Discarded", "Insufficient data to show a weekly trend.")
        else:
            pdf.add_info_box(label, "Missing", "No raw data found in exports.", (key == "glucose"))

    # SECTION 2: DETAILED ANALYSIS (Graphs + Tables)
    for key in valid_keys:
        pdf.add_page()
        label = target_metrics[key]
        pdf.chapter_title(f"2. {label} Weekly Breakdown")
        
        # Add Table
        csv_path = os.path.join(report_dir, f"summary_weekly_{key}.csv")
        df = pd.read_csv(csv_path).dropna()
        
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, "Weekly Average Values", 0, 1)
        pdf.cell(60, 7, "Week Starting", 1, 0, 'C'); pdf.cell(60, 7, "Average Value", 1, 1, 'C')
        
        pdf.set_font('Arial', '', 10)
        for _, row in df.iterrows():
            pdf.cell(60, 7, str(row.iloc[0]).split(" ")[0], 1, 0, 'C')
            pdf.cell(60, 7, f"{row.iloc[1]:.2f}", 1, 1, 'C')
        
        # Add Weekly Graph
        img_path = os.path.join(report_dir, f"weekly_{key}.png")
        if os.path.exists(img_path):
            pdf.ln(10)
            pdf.image(img_path, x=20, w=170)

    pdf.output(output_pdf)
    logging.info(f"✅ Detailed Report generated: {output_pdf}")