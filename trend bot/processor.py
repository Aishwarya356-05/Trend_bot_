import pandas as pd
from langdetect import detect, DetectorFactory
from datetime import datetime

# Ensure consistent language detection results
DetectorFactory.seed = 0

class DataProcessor:
    @staticmethod
    def clean_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 1 — CLEAN & NORMALIZE
        - Remove spam/duplicates
        - Normalize timestamps to daily granularity
        - Detect language and focus on English content
        """
        if df.empty:
            return df

        # Remove duplicates based on text
        df = df.drop_duplicates(subset=['text']).copy()

        # Normalize timestamps to daily granularity (YYYY-MM-DD)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')

        # Language Detection
        def is_english(text):
            try:
                return detect(text) == 'en'
            except:
                return False

        df = df[df['text'].apply(is_english)].copy()

        # Filter out very short texts which might be spam/non-informative
        df = df[df['text'].str.len() > 10].copy()

        return df
