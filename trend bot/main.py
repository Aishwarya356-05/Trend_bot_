import sys
import os
import json
import pandas as pd
import traceback

# Fix for UnicodeEncodeError on Windows when printing emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from processor import DataProcessor
from ml_engine import MLEngine
from insights import InsightsEngine, ChatbotEngine
from renderer import ReportRenderer

class TrendAnalyzerApp:
    def __init__(self, data_path='mock_data.json'):
        self.data_path = data_path
        self.processor = DataProcessor()
        self.ml_engine = MLEngine()
        self.insights_engine = InsightsEngine()
        self.renderer = ReportRenderer()
        self.df = None
        self.topic_stats = None
        self.business_insights = None

    def run_pipeline(self):
        # Load Data
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df_raw = pd.DataFrame(data)

        # Step 1: Clean & Normalize
        self.df = self.processor.clean_and_normalize(df_raw)

        # Step 2: Embedding & Clustering
        self.df = self.ml_engine.cluster_posts(self.df)

        # Step 3: Trend Detection
        self.topic_stats = self.ml_engine.analyze_trends(self.df)

        # Step 4: Summarization
        self.topic_stats = self.insights_engine.generate_summaries(self.topic_stats, self.df)

        # Step 5: Business Insights
        self.business_insights = self.insights_engine.get_business_insights(self.topic_stats)

        # Step 6: Generate Output
        self.report = self.renderer.render_daily_report(self.topic_stats, self.business_insights)
        self.dashboard_json = self.renderer.render_dashboard_json(self.topic_stats)

        # Initialize Chatbot
        self.chatbot = ChatbotEngine(self.ml_engine, self.topic_stats, self.df)

        return self.report, self.dashboard_json

    def chat_mode(self):
        print("\n" + "="*40)
        print("🤖 TRENDSAGE AI CHATBOT MODE")
        print("Ask anything about the report! (type 'exit' to quit)")
        print("="*40)
        
        while True:
            query = input("\nYou: ").lower()
            if query == 'exit':
                break
            
            response = self.chatbot.get_response(query)
            print(f"\nAI: {response}")

if __name__ == "__main__":
    try:
        app = TrendAnalyzerApp()
        print("Running Trend Analysis Pipeline...")
        report, db_json = app.run_pipeline()
        
        print("\nREPORT GENERATED:")
        # Force encode to utf-8 if printing to a pipe/file
        print(report.encode('utf-8', errors='replace').decode('utf-8'))
        
        print("\nDASHBOARD JSON PREVIEW (First Topic):")
        db_data = json.loads(db_json)
        if db_data['top_topics']:
            print(json.dumps(db_data['top_topics'][0], indent=2))
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

    # Optional: enter chat mode if run interactively
    if len(sys.argv) > 1 and sys.argv[1] == '--chat':
        app.chat_mode()
