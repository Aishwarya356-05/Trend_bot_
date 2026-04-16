import pandas as pd

class InsightsEngine:
    @staticmethod
    def generate_summaries(topic_stats: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 4 — SUMMARIZATION
        Generate concise executive summaries for top clusters.
        """
        summaries = []
        for topic, row in topic_stats.iterrows():
            cluster_df = df[df['topic'] == topic]
            top_post = cluster_df.sort_values(by='engagement', ascending=False).iloc[0]['text']
            platforms = ", ".join(row['platform'])
            dominant_sentiment = max(row['sentiment_label'], key=row['sentiment_label'].get)
            
            summary = (
                f"Topic centered around '{topic}', primarily discussed on {platforms}. "
                f"The sentiment is notably {dominant_sentiment}. "
                f"Key discussion point: \"{top_post[:100]}...\" "
                f"This topic is currently showing a {row['trend_label']} trend."
            )
            summaries.append(summary)
        
        topic_stats['summary'] = summaries
        return topic_stats

    @staticmethod
    def get_business_insights(topic_stats: pd.DataFrame) -> dict:
        """
        STEP 5 — BUSINESS INSIGHTS
        Provide risk alerts, opportunity signals with severity levels.
        """
        risk_alerts = []
        opportunities = []
        
        RISK_KEYWORDS = ['attack', 'outage', 'hacked', 'scam', 'leaked', 'vulnerability', 'alert', 'crisis', 'emergency', 'security']
        
        for topic, row in topic_stats.iterrows():
            neg_sentiment = row['sentiment_label'].get('negative', 0)
            vol = row['volume']
            topic_lower = topic.lower()
            
            # Keyword-based risk detection (high priority)
            contains_risk = any(kw in topic_lower for kw in RISK_KEYWORDS)
            
            # High Alert: Negative sentiment > 40% OR Risk Keywords + Moderate Volume
            if (neg_sentiment > 0.4 and (vol > 5 or row['trend_label'] == '🔥 Viral')) or (contains_risk and vol > 3):
                risk_alerts.append({
                    "topic": topic,
                    "severity": "CRITICAL",
                    "insight": f"CRITICAL: High priority risk detected on {topic}! Keywords/Sentiment indicate urgent threat.",
                    "action": "Immediate executive intervention and public statement required."
                })
            elif neg_sentiment > 0.25 or contains_risk:
                risk_alerts.append({
                    "topic": topic,
                    "severity": "MODERATE",
                    "insight": f"Moderate brand risk or security concern detected on {topic}.",
                    "action": "Monitor closely for the next 24 hours."
                })
            
            pos_sentiment = row['sentiment_label'].get('positive', 0)
            if pos_sentiment > 0.4 and row['trend_label'] in ['🔥 Viral', '📈 Emerging']:
                opportunities.append({
                    "topic": topic,
                    "insight": f"Strong positive signal for {topic}.",
                    "action": "Amplify via social channels immediately."
                })

        return {
            "risk_alerts": risk_alerts,
            "opportunities": opportunities
        }

class ChatbotEngine:
    def __init__(self, ml_engine, topic_stats, full_df):
        self.ml_engine = ml_engine
        self.topic_stats = topic_stats
        self.df = full_df

    def get_response(self, query):
        query = query.lower()
        
        # Conversational Greetings
        greetings = ['hi', 'hello', 'hey', 'hii', 'howdy', 'yo']
        if any(f" {g} " in f" {query} " for g in greetings) or query in greetings:
            return "Hello! I'm your TrendSage AI Assistant. I can summarize current trends, analyze sentiment, or compare different topics for you. What would you like to know about today's social data?"

        # Comparison logic
        if 'compare' in query:
            topics = self.topic_stats.index.tolist()
            matches = [t for t in topics if t.lower() in query]
            if len(matches) >= 2:
                t1, t2 = matches[0], matches[1]
                row1, row2 = self.topic_stats.loc[t1], self.topic_stats.loc[t2]
                return (f"Comparing **{t1}** and **{t2}**:\n\n"
                        f"- **Volume**: {t1} ({row1['volume']} posts) vs {t2} ({row2['volume']} posts)\n"
                        f"- **Sentiment**: {t1} is {max(row1['sentiment_label'], key=row1['sentiment_label'].get).title()} vs {t2} is {max(row2['sentiment_label'], key=row2['sentiment_label'].get).title()}\n"
                        f"- **Trend**: {t1} is {row1['trend_label']} vs {t2} is {row2['trend_label']}\n\n"
                        f"Overall, {t1 if row1['volume'] > row2['volume'] else t2} has a larger presence right now.")

        # Statistics and summary requests
        if any(w in query for w in ['summary', 'trending', 'hot', 'news', 'happen', 'what is up', 'headline', 'tell me about', 'update', 'analyze', 'report', 'data', 'top']):
            top_topics = self.topic_stats.head(6)
            insights = InsightsEngine.get_business_insights(self.topic_stats)
            alerts = insights['risk_alerts']
            
            response = "I've analyzed today's social data. Here are the top trending stories right now:\n\n"
            for topic, row in top_topics.iterrows():
                response += f"- **{topic}**: {row['trend_label']} ({row['volume']} posts) - {row['summary'][:80]}...\n"
            
            if alerts:
                critical = [a for a in alerts if a.get('severity') == 'CRITICAL']
                if critical:
                    response += f"\n🚨 **HIGH ALERT:** I've detected {len(critical)} critical risks! Check out **{critical[0]['topic']}** in the Risk Alerts section for immediate action."
                else:
                    response += f"\n⚠️ Note: I'm also tracking {len(alerts)} moderate brand risks."

            response += "\n\nWould you like me to dive deeper into any of these?"
            return response

        if any(w in query for w in ['alert', 'risk', 'warning', 'high alert', 'danger', 'help', 'bad', 'problem', 'issue']):
            insights = InsightsEngine.get_business_insights(self.topic_stats)
            alerts = insights['risk_alerts']
            if not alerts:
                return "The system is currently stable. No high-risk alerts detected in the current feed. Everything is looking good!"
            
            response = "⚠️ **ACTIVE SECURITY & BRAND ALERTS:**\n\n"
            for a in alerts:
                severity_icon = "🔴" if a.get('severity') == 'CRITICAL' else "🟡"
                response += f"{severity_icon} **{a['topic']}** ({a.get('severity')}):\n   {a['insight']}\n   **Action:** {a['action']}\n\n"
            return response

        # Platform info
        if 'platform' in query or 'where' in query:
            platforms = self.topic_stats['platform'].explode().unique()
            return f"I'm currently tracking data from: {', '.join(platforms)}. The highest activity is on Twitter and YouTube today!"
        
        # Sentiment info
        if 'sentiment' in query or 'mood' in query:
            return "Global sentiment is showing interesting patterns. We see strong positive vibes around Tech breakthroughs, but some high-risk negativity in Security and Finance sectors. Want a specific breakdown of a topic?"

        # Semantic Search in current data
        query_vec = self.ml_engine.get_embeddings([query])
        topics = self.topic_stats.index.tolist()
        topic_vecs = self.ml_engine.get_embeddings(topics)
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_vec, topic_vecs)[0]
        best_idx = similarities.argmax()
        
        # Lower threshold for better UX but high enough to avoid irrelevant answers
        if similarities[best_idx] > 0.35:
            best_topic = topics[best_idx]
            row = self.topic_stats.loc[best_topic]
            return (f"Regarding **{best_topic}**, here's what the data shows: {row['summary']} \n\n"
                    f"**Platform Activity:** {', '.join(row['platform'])} \n"
                    f"**Sentiment Profile:** {max(row['sentiment_label'], key=row['sentiment_label'].get).title()}.")
        
        # Friendly Fallback
        return (f"I don't see any specific trends for '{query}' in my current social feed. "
                f"However, I am currently tracking high activity on **{topics[0]}** and **{topics[1]}**. "
                f"Would you like to hear about those?")
