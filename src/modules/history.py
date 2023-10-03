import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime, timedelta
import time
import logging 
from modules.timesales import TimeSales

logger = logging.getLogger(__name__)

class History:
    def __init__(self):
        logger.info('Initializing history')

        self.id = 1
        self.base_url = 'https://links.sgx.com/1.0.0/derivatives-historical'
        self.target = 'TC.txt'
        self.path = 'logs'
        self.filename = os.path.join(self.path, 'history.json')

        if not os.path.exists(self.path):
            logger.info('Creating directory {}'.format(self.path))
            os.makedirs(self.path)
        
        logger.info('Initialized history')

    async def scrape_url(self, id, url, session):
        logger.info('Scraping URL {}'.format(url))
        async with session.get(url) as response:
            if response.status == 200:
                await response.text()
                filename = response.headers['content-disposition'].split('filename=')[1]
                
                if filename:
                    date = re.search(r'\d{8}', filename).group(0)                
                    date = datetime.strptime(date, '%Y%m%d').date().isoformat()

                    timesales = TimeSales(id, date, 'NOT_DOWNLOADED')
                    await self.save_url(timesales)
                else:
                    logger.error('No file found for {}'.format(url))            

    async def save_url(self, timesales):
        logger.info('Saving timesales for {}'.format(timesales.date))

        history = self.load_history()

        logger.debug('Removing timesales for {}'.format(timesales.date))
        history = [ts for ts in history if ts['id'] != timesales.id]
        
        logger.debug('Appending timesales for {}'.format(timesales.date))
        history.append(timesales.__dict__)
        history_sorted = sorted(history, key=lambda x: x['date'])

        logger.debug('Saving timesales')
        with open(self.filename, 'w') as history_file:
            json.dump(history_sorted, history_file, indent=4)

        logger.info('Saved timesales for {}'.format(timesales.date))

    async def get_timesales(self, step=100):
        logger.info('Scraping {} URLs'.format(step))

        start_time = time.time()

        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for _id in range(self.id, self.id + step):
                url = '{}/{}/{}'.format(self.base_url, _id, self.target)
                task = asyncio.create_task(self.scrape_url(_id, url, session))    
                tasks.append(task)

            self.id += step
            
            await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        logger.info('Finished scraping {} URLs in {} seconds'.format(step, end_time - start_time))

    def load_history(self):
        logger.info('Loading history')

        history = []
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as history_file:
                history = json.load(history_file)

                if len(history) > 0:
                    self.id = max([ts['id'] for ts in history]) + 1
                else :
                    self.id = 1
        
        else :
            with open(self.filename, 'w') as history_file:
                json.dump(history, history_file)

        logger.info('Loaded {} URLs'.format(len(history)))
        return history

    async def get_timesales_current(self):
        logger.info('Getting URLs for today')

        today = datetime.today().date().isoformat()
        is_weekday = datetime.today().weekday() < 5
        if not is_weekday:
            logger.debug('Today is a weekend, getting last weekday')
            # If today is a weekend, get the last weekday
            to_subtract = datetime.today().weekday() - 4
            today = datetime.today() - timedelta(days=to_subtract)
    
        is_today = False
        while not is_today:
            history = self.load_history()

            if len(history) == 0:
                logger.debug('No history found, getting 100 URLs')
                await self.get_timesales()
                await asyncio.sleep(10)

                continue
            
            # If today is a weekday and the last timesales is not today
            if history[-1]['date'] < '2013-5-10':  # Debugging
                logger.debug('Date of last timesales: {}'.format(history[-1]['date']))
                await self.get_timesales()

                logger.info('Sleeping for 10 seconds')
                await asyncio.sleep(10)
            else:
                logger.debug('Date found: {}'.format(history[-1]['date']))
                is_today = True

