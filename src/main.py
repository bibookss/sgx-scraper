import logging
from config import configure_logging
from modules import Download
import argparse
import sys
import asyncio

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download data from SGX')    
    parser.add_argument('--all', '-a', action='store_true', help='Download files from all dates')
    parser.add_argument('--today', '-t', action='store_true', help='Download files today')
    parser.add_argument('--today-until', '-tu', action='store_true', help='Download files from today until the end of time')
    parser.add_argument('--historical', '-hist', nargs='*', metavar=('START_DATE', 'END_DATE'), help='Fetch historical data for a date range (format: YYYYMMDD)')
    parser.add_argument('--log', '-l', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the log level (default: INFO)')    
    args = parser.parse_args()

    if len(sys.argv) == 1:
        logger.error('No arguments passed')
        parser.print_help(sys.stderr)
        sys.exit()

    if args.log:
        configure_logging(log_level=args.log)
    else:
        configure_logging()

    downloader = Download()
    if args.all:
        logger.info('Downloading files from all dates')
        asyncio.run(downloader.download_timesales_all())

    elif args.today:
        logger.info('Downloading files from today')
        asyncio.run(downloader.download_timesales_today())

    elif args.today_until:
        logger.info('Downloading files from today until the end of time')
        asyncio.run(downloader.download_timesales_from_today())

    elif args.historical:
        if len(args.historical) == 1:
            logger.info('Downloading historical files for {}'.format(args.historical[0]))
            start_date = args.historical[0]
            end_date = args.historical[0]

        elif len(args.historical) == 2:
            logger.info('Downloading historical files from {} to {}'.format(args.historical[0], args.historical[1]))
            start_date = args.historical[0]
            end_date = args.historical[1]

        asyncio.run(downloader.download_timesales_from_to(start_date, end_date))
