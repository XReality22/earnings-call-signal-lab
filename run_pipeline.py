"""Run the pipeline step by step:  python run_pipeline.py prices transcripts lm events analysis excel
Use  SIGNAL_LAB_DEMO=1 python run_pipeline.py demo lm events analysis excel  to test on synthetic data."""
import sys
sys.path.insert(0, "src")

def main(steps):
    for s in steps:
        print(f"\n=== {s} ===")
        if s == "demo":
            import make_demo_data; make_demo_data.run()
        elif s == "prices":
            import ingest_prices; ingest_prices.run()
        elif s == "transcripts":
            import ingest_transcripts; ingest_transcripts.run()
        elif s == "lm":
            import score_lm; score_lm.run()
        elif s == "finbert":
            import score_finbert; score_finbert.run()
        elif s == "llm":
            import score_llm; score_llm.run()
        elif s == "events":
            import events; events.run()
        elif s == "analysis":
            import analysis; analysis.run()
        elif s == "excel":
            import export_excel; export_excel.run()
        else:
            raise SystemExit(f"unknown step: {s}")

if __name__ == "__main__":
    main(sys.argv[1:] or ["prices", "transcripts", "lm", "events", "analysis", "excel"])
