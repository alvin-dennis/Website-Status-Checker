import subprocess
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import pandas as pd


def check_website_performance(url):
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()

        load_time = end_time - start_time
        status_code = response.status_code
        content_length = len(response.content)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "No title found"

        return {
            'url': url,
            'status_code': status_code,
            'load_time': load_time,
            'content_length': content_length,
            'title': title
        }
    except requests.RequestException as e:
        return {
            'url': url,
            'status_code': None,
            'load_time': None,
            'content_length': None,
            'title': str(e)
        }


def run_lighthouse(url):
    output_file = 'report.json'
    try:
        subprocess.run(['lighthouse', url, '--output=json', '--output-path', output_file], check=True)
        with open(output_file, 'r') as file:
            report = json.load(file)
        return report
    except subprocess.CalledProcessError as e:
        return {'error': str(e)}


def save_report(results, report_file):
    with open(report_file, 'w') as file:
        for row in results:
            file.write(f"{row}\n")
    return report_file


def create_performance_dataframe(urls):
    results = []
    for url in urls:
        results.append(check_website_performance(url))
    return pd.DataFrame(results)
