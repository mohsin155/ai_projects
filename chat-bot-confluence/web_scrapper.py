from idlelib.debugger_r import wrap_info

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse, urljoin
import csv
import json

from langsmith import expect


class WebScrapper:
    def __init__(self, delay=1):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def get_links_from_page(self, url, filter_domain=True):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if filter_domain:
                    if urlparse(full_url).netloc == urlparse(full_url).netloc:
                        links.append(full_url)
            else:
                links.append(full_url)
            return list(set(links))
        except Exception as e :
            print(f"Error getting links from {url}: {str(e)}")
            return []

    def scrape_page_content(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            content = {
                "url": url,
                "title": soup.title.string if soup.title else '',
                "headings" : [h.get_text().strip() for h in soup.find_all(["h1","h2","h3"])],
                "paragraphs" : [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip() != '' ],
                "full_text": soup.get_text().strip()
            }

            lines = (line.strip() for line in content["full_text"].splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content['full_text'] = ' '.join(chunk for chunk in chunks if chunk)

            return content
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def scrape_multiple_pages(self, urls):
        results = []

        for i, url in enumerate(urls, 1):
            print(f"Scraping {i}/{len(urls)} : {url}")

            content = self.scrape_page_content(url)
            if content:
                results.append(content)
            time.sleep(self.delay)
        return results

    def save_results(self, results, format='json', filename='scraped_data'):
        if(format == 'json'):
            with open(f'{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        elif format == 'csv':
            with open(f'{filename}.csv', 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=['url', 'title', 'full_text'])
                    writer.writeheader()
                    for result in results:
                        writer.writerow({
                            'url': result['url'],
                            'title': result['title'],
                            'full_text': result['full_text']
                        })
scraper = WebScrapper(delay=0)
discovered_links = scraper.get_links_from_page('https://evalueweb.com/')
print(f"Found {discovered_links} links")
result = scraper.scrape_multiple_pages(discovered_links)
scraper.save_results(result, format='json')
