import requests
from config import Config  
from newspaper import Article

class NewsService:
    """Handles fetching news articles from NewsAPI and scraping full content."""

    @staticmethod
    def get_news(topic):
        """Fetches latest news articles and extracts full text when possible."""
        url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={Config.NEWS_API_KEY}&pageSize=5"
        response = requests.get(url)

        if response.status_code == 200:
            articles = response.json().get("articles", [])
            formatted_articles = []

            for article in articles:
                article_url = article["url"]
                full_text = "Full text unavailable"

                try:
                    news_article = Article(article_url)
                    news_article.download()
                    news_article.parse()
                    full_text = news_article.text[:2000] + "..."  

                except Exception as e:
                    print(f"⚠️ Could not extract full text from {article_url}: {e}")

                formatted_articles.append(
                    f"🔹 **Title:** {article['title']}\n"
                    f"📰 **Source:** {article['source']['name']}\n"
                    f"📜 **Description:** {article.get('description', 'No description available.')}\n"
                    f"📝 **Full Article Text:** {full_text}\n"
                    f"🔗 **URL:** {article['url']}\n"
                    "------------------------------------------------------------"
                )
            print(f"\n🔍 NEWS API RESPONSE FOR TOPIC: {topic} (WITH FULL TEXT)\n")
            for article in formatted_articles:
                print(article)

            return "\n\n".join(formatted_articles)

        print("❌ No news found or API request failed.")
        return "No news found."
