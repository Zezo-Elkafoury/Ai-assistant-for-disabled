from googleapiclient.discovery import build

api_key = "YOUR_API_KEY"  # Replace with your actual API key

youtube = build("youtube", "v3", developerKey=api_key)

request = youtube.search().list(
    part="snippet",
    q="Osama Elzero",
    type="video",
    maxResults=50  # Adjust as needed
)

response = request.execute()

for item in response.get("items", []):
    print(f"Video Title: {item['snippet']['title']}")
    print(f"Video ID: {item['id']['videoId']}")
    print(f"Video URL: https://www.youtube.com/watch?v={item['id']['videoId']}")
    print("-" * 20)