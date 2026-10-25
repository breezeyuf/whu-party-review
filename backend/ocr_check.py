"""Run a real OCR inference check; exits nonzero when recognition fails."""
import json
import multiprocessing


def main():
    import config  # Load the same backend/.env as the application.
    from ai.ocr import probe, shutdown
    try:
        result = probe()
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return 0 if result["ok"] else 1
    finally:
        shutdown()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
