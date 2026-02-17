import logging
from src.utils import load_config, setup_logging
from src.ingestion import process_subject
from src.analysis import analyze_subject
from src.reporting import generate_pdf_report

def main():
    # 1. Setup
    setup_logging()
    config = load_config()
    
    logging.info(" Starting Data Preprocessing Pipeline")

    # 2. Get subjects from config
    subjects = config['settings']['subjects']

    # 3. Iterate and Process
    for subject in subjects:
        try:
            # Step 1: Ingestion & Cleaning
            process_subject(subject, config)

            # Step 2: Analysis & Reporting
            analyze_subject(subject, config)

            # Step 3: (Optional) PDF Report Generation - Can be added here if needed
            generate_pdf_report(subject, config)

        except Exception as e:
            logging.error(f" Critical error processing {subject}: {e}")

    logging.info(" Pipeline execution finished.")

if __name__ == "__main__":
    main()