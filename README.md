# Data Team Mini Project
The Data Team Mini Project is a Python CLI application that downloads daily derivate data from the SGX website. 

## Features
1. Option to download data starting today until the app closes, or to download all files from the start until the app closes.
2. Download data from a given date range.
3. Offers logging options. 
4. Redownloads files.

## Installation
```
pip install -r requirements.txt
```

## Usage
```
python3 main.py [-h] [--all] [--today] [--historical [START_DATE [END_DATE ...]]] [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
```