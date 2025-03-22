from datetime import datetime, timedelta
from database import Database
from market_analyzer import MarketAnalyzer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_daily_data():
    """
    Process market data for the last 24 hours and store it in the database
    """
    try:
        # Initialize components
        database = Database()
        market_analyzer = MarketAnalyzer()
        
        # Get data from the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # Get posts and comments
        posts = database.get_posts_by_time_range(start_time, end_time)
        comments = database.get_comments_by_time_range(start_time, end_time)
        
        # Process the data
        analysis = market_analyzer.analyze_market_trends(posts, comments)
        
        # Store in database
        database.store_daily_analysis(
            date=end_time.date(),
            stock_mentions=analysis["stock_mentions"],
            word_frequencies=analysis["word_frequencies"],
            fear_greed_index=analysis["fear_greed_index"],
            market_sentiment=analysis["batch_analysis"]["market_sentiment"],
            trending_topics=analysis["batch_analysis"]["trending_topics"],
            risk_indicators=analysis["batch_analysis"]["risk_indicators"]
        )
        
        logger.info(f"Successfully processed and stored market data for {end_time.date()}")
        
    except Exception as e:
        logger.error(f"Error processing daily data: {str(e)}")
        raise

if __name__ == "__main__":
    process_daily_data() 