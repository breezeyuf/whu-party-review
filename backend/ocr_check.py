"""Run the same real RapidOCR inference probe as the settings page."""
import argparse
import json
import multiprocessing


def main(argv=None):
    import config  # Load backend/.env and the normal runtime paths.
    from ai.ocr import probe, shutdown
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',choices=('auto','rapidocr','none'),default='rapidocr')
    parser.add_argument('--timeout-s',type=int,default=120)
    parser.add_argument('--dpi',type=int,default=200)
    args=parser.parse_args(argv)
    if not 1<=args.timeout_s<=600 or not 72<=args.dpi<=300:
        parser.error('timeout-s must be 1..600; dpi must be 72..300')
    try:
        result=probe({'engine':args.engine,'timeout_s':args.timeout_s,'min_dpi':args.dpi})
        print(json.dumps(result,ensure_ascii=False),flush=True)
        return 0 if result['ok'] else 1
    finally:
        shutdown()


if __name__=='__main__':
    multiprocessing.freeze_support()
    raise SystemExit(main())
