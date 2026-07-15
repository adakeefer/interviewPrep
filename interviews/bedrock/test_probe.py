from pathlib import Path
from logarithm import Logarithm
import argparse
from datetime import datetime


TEST_FILE = "logs/test_00000.log"


def load_logarithm():
    logger = Logarithm()
    logger.build_index()
    #print([str(log) for log in logger.logs])
    
    return logger

    
'''
2025-02-28T23:58:23.232000Z DEBUG auth-service Background task scheduled: 903f967f-830f-4da1-b4a4-4a5f99b9cfc6
2025-02-28T23:58:47.424000Z DEBUG auth-service Background task scheduled: 3ed96328-aea3-49dd-9739-3b3b0ecb7d2d
2025-02-28T23:59:11.616000Z DEBUG app-service Data validation complete: 80db87a9-4b14-4fa1-95d8-dd50135e0dbf [response_time=344ms]
2025-02-28T23:59:35.808000Z ERROR payment-service Resource not found: ee9e77e8-54ed-46bd-82d8-5ac4ed62ee77

'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", type=str, default=None, help="target log level.")
    parser.add_argument("--service", type=str, default=None, help="target service")
    parser.add_argument("--start_time", type=str, default=None, help="start_time")
    parser.add_argument("--end_time", type=str, default=None, help="end_time")
    args = parser.parse_args()

    if (args.start_time and not args.end_time) or (args.end_time and not args.start_time):
        print("start time and end time must be supplied together")
        return

    # other input parsing

    logger = load_logarithm()
    time_end = datetime.fromisoformat(args.end_time) if args.end_time is not None else args.end_time
    time_start = datetime.fromisoformat(args.start_time) if args.start_time is not None else args.start_time


    res = logger.search(target_log_level=args.log_level, target_service=args.service, target_time_end=time_end, target_time_start=time_start)
    print(len(res))






if __name__ == "__main__":
    main()