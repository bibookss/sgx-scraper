import logging
import os
import json
import asyncio
import aiohttp
from datetime import datetime
from modules.history import History
from modules.timesales import TimeSales
import time

logger = logging.getLogger(__name__)

class Download:
    def __init__(self):
        logger.info('Initializing downloader')

        self.path = 'data'
        self.history = History()

        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        asyncio.run(self.history.get_timesales_current())

        logger.info('Downloader initialized')
    
    async def download_url(self, timesales, num):
        logger.info('Downloading file {} of {} for {}'.format(num + 1, len(timesales['urls']), timesales['date']))

        url = timesales['urls'][num]
        destination = os.path.join(self.path, timesales['date'], url.split('/')[-1])
                                   
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logger.debug('Downloading file from {}'.format(url))
                if response.status == 200:
                    logger.debug('Saving file to {}'.format(destination))

                    with open(destination, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
                    
                    timesales['status'] = 'DOWNLOADED'
                else:
                    logger.error('Failed to download file from {}.Status code: {}'.format(url, response.status))
                    timesales['status'] = 'FAILED'

                await self.history.save_url(TimeSales(timesales['id'], timesales['date'], timesales['status']))
                
    async def download_timesales(self, timesales):
        start_time = time.time()

        timesales_path = os.path.join(self.path, timesales['date'])
        if not os.path.exists(timesales_path):
            os.makedirs(timesales_path)

        tasks = []
        for num in range(len(timesales['urls'])):
            task = asyncio.create_task(self.download_url(timesales, num))
            tasks.append(task)

        await asyncio.gather(*tasks)

        end_time = time.time()
        logger.info('Finished downloading files for {}. Time taken: {} seconds'.format(timesales['date'], end_time - start_time))

    async def download_timesales_today(self):
        logger.info('Downloading files for today')

        with open(self.history.filename, 'r') as history_file:
            history = json.load(history_file)
        
        today = datetime.today().date().isoformat()
        for timesales in history:
            if timesales['date'] == today:
                if timesales['status'] == 'NOT_DOWNLOADED':
                    await self.download_timesales(timesales)
                else:
                    logger.info('Files for today have already been downloaded')
        
        logger.info('Finished downloading files for today')

        await self.redownload_failed()

    async def download_timesales_from_to(self, from_date, to_date):
        # Validate dates
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            logger.error('Invalid date format')
            return

        # Start date must be before end date
        if from_date > to_date:
            logger.error('Start date must be before end date')
            return

        logger.info('Downloading files from {} to {}'.format(from_date, to_date))

        with open(self.history.filename, 'r') as history_file:
            history = json.load(history_file)
        
        for timesales in history:
            if timesales['date'] >= from_date and timesales['date'] <= to_date:
                if timesales['status'] == 'NOT_DOWNLOADED':
                    await self.download_timesales(timesales)
                else:
                    logger.info('Files for {} have already been downloaded'.format(timesales['date']))

        logger.info('Finished downloading files from {} to {}'.format(from_date, to_date))

        await self.redownload_failed()

    async def download_timesales_from_today(self):
        logger.info('Downloading files from today')

        while True:
            await self.download_timesales_today()

            # Sleep until tomorrow
            logger.info('Sleeping until tomorrow')
            await asyncio.sleep(86400)

            # Redownload failed files
            await self.redownload_failed()

    async def download_timesales_all(self):
        logger.info('Downloading all files')

        while True:
            with open(self.history.filename, 'r') as history_file:
                history = json.load(history_file)

            for timesales in history:
                if timesales['status'] == 'NOT_DOWNLOADED':
                    await self.download_timesales(timesales)
                else:
                    logger.info('Files for {} have already been downloaded'.format(timesales['date']))

            logger.info('Finished downloading all files for today')

            # Sleep until tomorrow
            logger.info('Sleeping until tomorrow')
            await asyncio.sleep(86400)
            
            await self.redownload_failed()

    async def redownload_failed(self):
        logger.info('Redownloading failed files')

        with open(self.history.filename, 'r') as history_file:
            history = json.load(history_file) 

        for timesales in history:
            if timesales['status'] == 'FAILED':
                logger.debug('Redownloading failed file for {}'.format(timesales['date']))
                await self.download_timesales(timesales)       

        logger.info('Finished redownloading failed files')