import json
from datetime import datetime

class ReportRenderer:
    @staticmethod
    def render_daily_report(topic_stats, business_insights):
        """
        STEP 6 — OUTPUT FORMAT (Report)
        """
        report = []
        report.append("==============================")
        report.append("📊 DAILY TREND REPORT")
        report.append("==============================\n")

        # Viral Topics
        viral = topic_stats[topic_stats['trend_label'] == '🔥 Viral']
        if not viral.empty:
            report.append("🔥 Top Viral Topics:")
            for i, (topic, row) in enumerate(viral.head(3).iterrows(), 1):
                report.append(f"{i}. {topic}")
                report.append(f"   - Platforms: {', '.join(row['platform'])}")
                report.append(f"   - Volume: {row['volume']}")
                sentiment_str = ", ".join([f"{k}: {v*100:.1f}%" for k, v in row['sentiment_label'].items()])
                report.append(f"   - Sentiment: {sentiment_str}")
                report.append(f"   - Engagement: {row['engagement']}")
                report.append(f"   - Summary: {row['summary']}")
                
                # Associated insight if any
                insight = next((bi['insight'] for bi in business_insights['opportunities'] if bi['topic'] == topic), "No specific insight.")
                report.append(f"   - Business Insight: {insight}")
                report.append("")

        # Emerging Topics
        emerging = topic_stats[topic_stats['trend_label'] == '📈 Emerging']
        if not emerging.empty:
            report.append("📈 Emerging Topics:")
            for i, (topic, row) in enumerate(emerging.head(3).iterrows(), 1):
                report.append(f"{i}. {topic} (Growth: {row['growth_rate']*100:.1f}%)")
            report.append("")

        # Risk Alerts
        if business_insights['risk_alerts']:
            report.append("⚠ Risk Alerts:")
            for alert in business_insights['risk_alerts']:
                report.append(f"- {alert['insight']}")
                report.append(f"  Action: {alert['action']}")
            report.append("")

        # Opportunities
        if business_insights['opportunities']:
            report.append("💡 Opportunities:")
            for opp in business_insights['opportunities']:
                report.append(f"- {opp['insight']}")
                report.append(f"  Action: {opp['action']}")
            report.append("")

        return "\n".join(report)

    @staticmethod
    def render_dashboard_json(topic_stats):
        """
        STEP 6 — OUTPUT FORMAT (JSON)
        """
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "top_topics": []
        }
        
        for topic, row in topic_stats.iterrows():
            data["top_topics"].append({
                "topic": topic,
                "platforms": row['platform'],
                "volume": int(row['volume']),
                "engagement_rate": float(row['engagement_rate']),
                "sentiment_distribution": {k: float(v) for k, v in row['sentiment_label'].items()},
                "growth_rate": float(row['growth_rate']),
                "trend_label": row['trend_label']
            })
            
        return json.dumps(data, indent=2)
