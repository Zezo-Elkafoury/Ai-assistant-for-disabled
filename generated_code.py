import requests
from bs4 import BeautifulSoup
import csv

try:
    url = "https://en.wikipedia.org/wiki/List_of_most_popular_websites"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="wikitable")

    urls = []
    for row in table.find_all("tr")[1:4]:  # Extract top 3
        cells = row.find_all("td")
        if cells and cells[1].find("a"):
            url = cells[1].find("a").get("href")
            if url.startswith("//"): # Handle protocol-relative URLs
                url = "https:" + url
            urls.append(url)


    with open("top_websites.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for url in urls:
            writer.writerow([url])

except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
except Exception as e:
    print(f"An error occurred: {e}")