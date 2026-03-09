import os
import logging
import pandas as pd
from datetime import datetime
from fpdf import FPDF


class PDFReport(FPDF):
    """Custom FPDF class for FitBit health reports."""

    def __init__(self, subject_name="Unknown"):
        super().__init__()
        self.subject_name = subject_name

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Fitbit Consolidated Health Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, 5, f'Subject: {self.subject_name}', 0, 1, 'C')
        self.ln(3)

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
        """Fix #10: Critical items get bold red text + darker red background."""
        if critical:
            self.set_fill_color(255, 200, 200)
            self.set_text_color(180, 0, 0)
        else:
            self.set_fill_color(245, 245, 245)
            self.set_text_color(0, 0, 0)

        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, f"Metric: {label}", 'TLR', 1, 'L', 1)
        self.set_font('Arial', 'I', 9)
        self.multi_cell(0, 6, f"Status: {status}\nReason: {reason}", 'BLR', 'L', 1)
        self.set_text_color(0, 0, 0)  # Reset text color
        self.ln(3)

    def add_executive_summary(self, report_dir, target_metrics):
        """Fix #11: Add an executive summary page with metadata and methodology."""
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Executive Summary', 0, 1, 'L')
        self.ln(3)

        # Report metadata
        self.set_font('Arial', '', 10)
        self.cell(0, 7, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
        self.cell(0, 7, f"Subject Identifier: {self.subject_name}", 0, 1)

        # Determine data date range from available CSVs
        date_min, date_max = None, None
        for key in target_metrics:
            csv_path = os.path.join(report_dir, f"summary_weekly_{key}.csv")
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                    if not df.empty:
                        if date_min is None or df.index.min() < date_min:
                            date_min = df.index.min()
                        if date_max is None or df.index.max() > date_max:
                            date_max = df.index.max()
                except Exception:
                    pass

        if date_min and date_max:
            self.cell(0, 7,
                      f"Data Range: {date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}",
                      0, 1)
        else:
            self.cell(0, 7, "Data Range: Not available", 0, 1)

        self.ln(5)

        # Methodology
        self.set_font('Arial', 'B', 11)
        self.cell(0, 7, 'Methodology', 0, 1)
        self.set_font('Arial', '', 10)
        methodology = (
            "This report summarizes physiological data collected from a Fitbit wearable device. "
            "Raw sensor data was cleaned (duplicate removal, date standardization, median imputation "
            "for missing values) and then aggregated into weekly and monthly averages. Charts display "
            "time-series trends for each available health metric. Missing values in the original data "
            "were imputed using per-column median to avoid introducing biologically impossible values."
        )
        self.multi_cell(0, 6, methodology)
        self.ln(5)

        # Units reference
        self.set_font('Arial', 'B', 11)
        self.cell(0, 7, 'Common Units Reference', 0, 1)
        self.set_font('Arial', '', 9)
        units = [
            ("Heart Rate", "Beats per minute (BPM)"),
            ("HRV (RMSSD)", "Milliseconds (ms)"),
            ("SpO2 / Oxygen Saturation", "Percentage (%)"),
            ("Sleep Score", "0-100 composite score"),
            ("Stress Score", "0-100 composite score"),
            ("Activity (Steps)", "Count"),
            ("Glucose", "mg/dL"),
        ]
        for metric, unit in units:
            self.cell(60, 6, f"  {metric}:", 0, 0)
            self.cell(0, 6, unit, 0, 1)
        self.ln(5)


def _render_data_table(pdf, csv_path):
    """Fix #8: Render ALL columns from a CSV with proper headers.
    Fix #21: Wrap formatting in try/except to handle non-numeric values.
    """
    try:
        df = pd.read_csv(csv_path).dropna()
    except Exception as e:
        logging.warning(f"Could not read CSV for table: {e}")
        return

    if df.empty:
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 7, "No data available.", 0, 1)
        return

    columns = df.columns.tolist()
    first_col = columns[0]
    other_cols = columns[1:]
    
    max_other_cols = 6
    if not other_cols:
        col_chunks = [[]]
    else:
        col_chunks = [other_cols[i:i + max_other_cols] for i in range(0, len(other_cols), max_other_cols)]

    page_width = 180

    for chunk in col_chunks:
        current_cols = [first_col] + chunk
        n_cols = len(current_cols)
        col_width = page_width / max(n_cols, 1)

        # Table header
        pdf.set_font('Arial', 'B', 8)
        for col_name in current_cols:
            # Clean up column name for display
            display_name = col_name.replace('_', ' ').title()
            if len(display_name) > 15:
                display_name = display_name[:14] + '.'
            pdf.cell(col_width, 7, display_name, 1, 0, 'C')
        pdf.ln()

        # Table rows
        pdf.set_font('Arial', '', 8)
        for _, row in df.iterrows():
            for col_name in current_cols:
                val = row[col_name]
                # Fix #21: Safe formatting
                try:
                    if isinstance(val, (int, float)):
                        cell_text = f"{val:.2f}"
                    else:
                        cell_text = str(val).split(" ")[0] if col_name == first_col else str(val)
                except (ValueError, TypeError):
                    cell_text = str(val)

                if len(cell_text) > 15:
                    cell_text = cell_text[:14] + '.'
                pdf.cell(col_width, 7, cell_text, 1, 0, 'C')
            pdf.ln()

            # Page break if we're running out of space
            if pdf.get_y() > 260:
                pdf.add_page()
                
        # Add space after each table chunk
        pdf.ln(5)


def _render_metric_section(pdf, section_num, key, label, report_dir, freq_label):
    """Render a single metric section (weekly or monthly) in the PDF."""
    csv_path = os.path.join(report_dir, f"summary_{freq_label}_{key}.csv")
    img_path = os.path.join(report_dir, f"{freq_label}_{key}.png")

    pdf.add_page()
    pdf.chapter_title(f"{section_num}. {label} {freq_label.capitalize()} Breakdown")

    # Table
    if os.path.exists(csv_path):
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, f"{freq_label.capitalize()} Average Values", 0, 1)
        _render_data_table(pdf, csv_path)

    # Chart
    if os.path.exists(img_path):
        pdf.ln(5)
        pdf.image(img_path, x=10, w=180)


def generate_pdf_report(subject_name, config):
    """Generate a comprehensive PDF health report for a subject.

    Fixes: #6 (monthly data), #7 (section numbering), #8 (all columns),
    #10 (critical styling), #11 (executive summary), #16 (config paths),
    #21 (safe value formatting).
    """
    # Fix #16: Use config paths instead of hardcoded
    report_dir = os.path.join(
        config['paths'].get('reports_dir', 'reports'), subject_name
    )
    output_pdf = os.path.join(report_dir, f"{subject_name}_Detailed_Report.pdf")

    # Skip if already processed and force_rerun is not enabled
    force_rerun = config['settings'].get('force_rerun', False)
    if not force_rerun and os.path.exists(output_pdf):
        logging.info(f"   ⏭  Skipping report for {subject_name} (PDF already exists. Set force_rerun: true to regenerate)")
        return

    target_metrics = {
        "glucose": "Glucose", "heart_rate": "Heart Rate",
        "hrv": "Heart Rate Variability",
        "sleep_score": "Sleep Score", "stress_score": "Stress Score",
        "oxygen": "Oxygen Saturation", "activity": "Physical Activity"
    }

    pdf = PDFReport(subject_name=subject_name)
    pdf.add_page()

    # Fix #11: Executive summary page
    pdf.add_executive_summary(report_dir, target_metrics)

    # Section 1: Data Quality Assessment
    pdf.add_page()
    pdf.chapter_title("1. Data Quality Assessment")

    valid_keys = []
    if not os.path.exists(report_dir):
        return
    files = os.listdir(report_dir)

    for key, label in target_metrics.items():
        csv_file = f"summary_weekly_{key}.csv"

        if csv_file in files:
            try:
                df = pd.read_csv(os.path.join(report_dir, csv_file)).dropna()
            except Exception:
                df = pd.DataFrame()

            if len(df) >= 2:
                valid_keys.append(key)
                pdf.add_info_box(label, "Valid",
                                 f"Successfully processed {len(df)} weeks of data.")
            else:
                pdf.add_info_box(label, "Discarded",
                                 "Insufficient data to show a weekly trend (< 2 weeks).")
        else:
            pdf.add_info_box(label, "Missing",
                             "No raw data found in exports.",
                             critical=(key == "glucose"))

    # Fix #7: Dynamic section numbering
    section_num = 2

    # Detailed Analysis sections — weekly AND monthly (Fix #6)
    for key in valid_keys:
        label = target_metrics[key]

        # Weekly section
        _render_metric_section(pdf, section_num, key, label, report_dir, "weekly")
        section_num += 1

        # Fix #6: Monthly section (only if data exists)
        monthly_csv = os.path.join(report_dir, f"summary_monthly_{key}.csv")
        monthly_img = os.path.join(report_dir, f"monthly_{key}.png")
        if os.path.exists(monthly_csv) or os.path.exists(monthly_img):
            _render_metric_section(pdf, section_num, key, label, report_dir, "monthly")
            section_num += 1

    pdf.output(output_pdf)
    logging.info(f"✅ Detailed Report generated: {output_pdf}")