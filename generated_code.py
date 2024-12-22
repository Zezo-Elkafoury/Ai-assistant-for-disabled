import requests
from bs4 import BeautifulSoup
from newspaper import Article
from transformers import pipeline
import smtplib
from email.mime.text import MIMEText
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuration (replace with your actual values)
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"
RECIPIENT_EMAIL = "recipient_email@example.com"
GOOGLE_SHEET_NAME = "Python Articles"
CREDENTIALS_FILE = "your_credentials.json"

# Blog URLs
BLOGS = [
    "https://realpython.com/blog/",
    # Add more blog URLs here
]


def fetch_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    article_links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and ("/python/" in href or "/tutorial/" in href):  # Adjust keywords as needed
            if href.startswith("/"):
                article_links.append(url + href[1:])
            else:
                article_links.append(href)
    return article_links


def summarize_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        summarizer = pipeline("summarization")
        summary = summarizer(article.text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
        return summary
    except Exception as e:
        print(f"Error summarizing {url}: {e}")
        return None



def format_email(summaries):
    email_body = f"Python Articles Summary - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    for url, summary in summaries.items():
        email_body += f"**{url}**\n{summary}\n\n"
    return email_body



def save_to_google_sheet(summaries, email_draft):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    data = [[url, summary] for url, summary in summaries.items()]
    data.insert(0, ["URL", "Summary"])
    sheet.clear()
    sheet.update('A1', data)
    sheet.update_acell('A1', "URL")
    sheet.update_acell('B1', "Summary")
    sheet.update_acell('C1', "Email Draft")
    sheet.update_acell('C2', email_draft)

    sheet_url = sheet.spreadsheet.url
    return sheet_url


def send_notification(sheet_url):
    msg = MIMEText(f"Python articles summarized and saved! View the sheet here: {sheet_url}")
    msg['Subject'] = "Python Article Summaries Ready"
    msg['From'] = EMAIL_USER
    msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)


if __name__ == "__main__":
    all_summaries = {}
    for blog_url in BLOGS:
        article_links = fetch_articles(blog_url)
        for link in article_links:
            summary = summarize_article(link)
            if summary:
                all_summaries[link] = summary

    email_draft = format_email(all_summaries)
    sheet_url = save_to_google_sheet(all_summaries, email_draft)
    send_notification(sheet_url)