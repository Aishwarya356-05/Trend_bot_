import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from textblob import TextBlob
import collections
import re

STOP_WORDS = {
    'this', 'that', 'with', 'from', 'about', 'your', 'just', 'more', 'what', 'their',
    'there', 'these', 'those', 'will', 'some', 'could', 'should', 'would', 'been',
    'being', 'have', 'were', 'also', 'only', 'very', 'here', 'when', 'into', 'after',
    'over', 'than', 'under', 'only', 'even', 'most', 'such', 'well', 'many', 'back',
    'much', 'down', 'through', 'must', 'before'
}

class MLEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, texts):
        return self.model.encode(texts)

    def cluster_posts(self, df: pd.DataFrame, n_clusters=None) -> pd.DataFrame:
        """
        STEP 2 — EMBEDDING & CLUSTERING
        - Group posts into semantic clusters
        - Assign a short descriptive topic label to each cluster
        """
        if df.empty:
            return df

        texts = df['text'].tolist()
        embeddings = self.get_embeddings(texts)

        # Heuristic for number of clusters if not provided
        if n_clusters is None:
            n_clusters = max(3, min(len(df) // 2, 12))

        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init='auto')
        df['cluster'] = kmeans.fit_predict(embeddings)

        # Generate topic labels (simplified: most common words in cluster)
        cluster_labels = {}
        for i in range(n_clusters):
            cluster_texts = df[df['cluster'] == i]['text'].str.cat(sep=' ')
            # Filter out punctuation and short words, and common stop words
            import re
            words = re.findall(r'\b\w{4,}\b', cluster_texts.lower())
            words = [w for w in words if w not in STOP_WORDS]
            
            most_common = collections.Counter(words).most_common(2)
            label = " & ".join([w[0] for w in most_common]) if most_common else f"Topic {i}"
            cluster_labels[i] = label.title()

        df['topic'] = df['cluster'].map(cluster_labels)
        return df

    def analyze_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 3 — TREND DETECTION
        For each cluster compute metrics and mark trend labels.
        """
        if df.empty:
            return pd.DataFrame()

        # Sentiment Analysis
        df['sentiment_score'] = df['text'].apply(lambda x: TextBlob(x).sentiment.polarity)
        def label_sentiment(score):
            if score > 0.1: return 'positive'
            elif score < -0.1: return 'negative'
            else: return 'neutral'
        df['sentiment_label'] = df['sentiment_score'].apply(label_sentiment)

        # Group by topic (cluster)
        topic_stats = df.groupby('topic').agg({
            'text': 'count',
            'engagement': 'sum',
            'platform': lambda x: list(set(x)),
            'sentiment_label': lambda x: x.value_counts(normalize=True).to_dict()
        }).rename(columns={'text': 'volume'})

        topic_stats['engagement_rate'] = topic_stats['engagement'] / topic_stats['volume']
        
        # Simulating growth rate for trend detection
        # Use engagement rate as a base for growth to make it more 'trained' by data
        topic_stats['growth_rate'] = (topic_stats['engagement_rate'] / 10000).clip(-0.5, 1.5)

        def get_trend_label(row):
            if row['growth_rate'] > 0.8: return '🔥 Viral'
            elif row['growth_rate'] > 0.2: return '📈 Emerging'
            elif row['growth_rate'] < -0.1: return '📉 Declining'
            else: return '🧊 Stable'

        topic_stats['trend_label'] = topic_stats.apply(get_trend_label, axis=1)

        # Rank clusters by volume + engagement growth (simplified as volume * growth)
        topic_stats['rank_score'] = topic_stats['volume'] * (1 + topic_stats['growth_rate'])
        topic_stats = topic_stats.sort_values(by='rank_score', ascending=False)

        return topic_stats
