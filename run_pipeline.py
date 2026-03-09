import sys
import logging
from src.utils import load_config, setup_logging
from src.ingestion import process_subject
from src.analysis import analyze_subject
from src.reporting import generate_pdf_report


def main():
    """Run the full FitBit data pipeline.

    Fix #18: Tracks successes/failures per subject and reports a summary.
    Sets non-zero exit code if any subject failed.
    """
    # 1. Setup
    setup_logging()
    config = load_config()

    logging.info("═" * 60)
    logging.info(" Starting FitBit Data Processing Pipeline")
    logging.info("═" * 60)

    # 2. Get subjects from config
    subjects = config['settings']['subjects']
    logging.info(f" Subjects to process: {subjects}")

    # 3. Track results
    successes = []
    failures = []

    # 4. Iterate and Process
    for subject in subjects:
        try:
            logging.info(f"\n{'─' * 40}")
            logging.info(f" Processing: {subject}")
            logging.info(f"{'─' * 40}")

            # Step 1: Ingestion & Cleaning
            process_subject(subject, config)

            # Step 2: Analysis & Visualization
            analyze_subject(subject, config)

            # Step 3: PDF Report Generation
            generate_pdf_report(subject, config)

            successes.append(subject)
            logging.info(f" ✅ {subject} completed successfully")

        except Exception as e:
            failures.append((subject, str(e)))
            logging.error(f" ❌ Critical error processing {subject}: {e}", exc_info=True)

    # 5. Summary
    logging.info(f"\n{'═' * 60}")
    logging.info(" Pipeline Execution Summary")
    logging.info(f"{'═' * 60}")
    logging.info(f" Total subjects: {len(subjects)}")
    logging.info(f" Successful:     {len(successes)}")
    logging.info(f" Failed:         {len(failures)}")

    if successes:
        logging.info(f" Succeeded: {', '.join(successes)}")
    if failures:
        logging.error(" Failed subjects:")
        for subj, err in failures:
            logging.error(f"   - {subj}: {err}")

    logging.info(f"{'═' * 60}")

    # Non-zero exit code if any subject failed
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()