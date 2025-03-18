# MarketMood

MarketMood is a SaaS platform that analyzes retail investor sentiment across social media platforms to provide valuable market insights.

## Project Overview

MarketMood collects and analyzes data from various social media platforms (starting with Reddit) to:

- Track retail investor discussions
- Identify trending stocks
- Analyze market sentiment
- Detect fear/greed indicators
- Provide market direction insights

## Project Structure

```
marketmood/
├── src/           # Source code
├── data/          # Data storage
├── tests/         # Test files
├── config/        # Configuration files
└── docs/          # Documentation
```

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run the development server: `python src/main.py`

## Technologies Used

- Python for data collection and analysis
- Reddit API for data collection
- DeepSeek for sentiment analysis
- Supabase for database and authentication
- Vercel for deployment
- FastAPI for backend API

## Getting Started

1. Create a Reddit API account at https://www.reddit.com/prefs/apps
2. Set up a Supabase account at https://supabase.com
3. Create a Vercel account at https://vercel.com
4. Follow the setup instructions in the docs folder

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
