"""
AI Engine - Claude AI Integration
Generates insights, recommendations, and natural language analysis
"""

import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional
import json
from app_config import INDUSTRY_PROMPTS, AI_PROVIDERS
from enterprise_db import get_api_key

# ============ CLAUDE AI INTEGRATION ============
def call_claude_api(user_id: int, prompt: str, max_tokens: int = 1000) -> Tuple[bool, str]:
    """Call Claude API with user's key"""
    try:
        from anthropic import Anthropic
        
        # Get user's Claude API key
        api_key = get_api_key(user_id, 'claude')
        
        if not api_key:
            return False, "❌ Claude API key not configured. Please add it in Settings."
        
        client = Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text if message.content else ""
        return True, response_text
        
    except Exception as e:
        return False, f"❌ Error calling Claude: {str(e)}"

# ============ INDUSTRY ANALYSIS ============
def analyze_with_claude(user_id: int, df: pd.DataFrame, industry: str) -> Tuple[bool, str]:
    """Analyze data using Claude for specific industry"""
    try:
        # Get industry prompt
        prompt_template = INDUSTRY_PROMPTS.get(industry, INDUSTRY_PROMPTS['solar'])
        
        # Prepare data summary
        data_summary = f"""
        Dataset Summary:
        - Records: {len(df)}
        - Columns: {len(df.columns)}
        - Column names: {', '.join(df.columns.tolist())}
        
        Data Preview:
        {df.head(10).to_string()}
        
        Statistical Summary:
        {df.describe().to_string()}
        
        {prompt_template}
        """
        
        success, response = call_claude_api(user_id, data_summary)
        return success, response
        
    except Exception as e:
        return False, f"Error analyzing data: {str(e)}"

# ============ RECOMMENDATION GENERATION ============
def generate_ai_recommendations(user_id: int, df: pd.DataFrame, industry: str, 
                               analysis_results: Dict) -> List[Dict]:
    """Generate AI-powered recommendations"""
    try:
        prompt = f"""
Based on the following {industry} industry data analysis:

Data Summary:
- Total Records: {len(df)}
- Columns: {', '.join(df.columns.tolist())}

Analysis Results:
{json.dumps(analysis_results, indent=2, default=str)}

Data Sample:
{df.head(5).to_string()}

Please provide 5-7 specific, actionable recommendations in JSON format:
{{
    "recommendations": [
        {{
            "title": "Recommendation Title",
            "description": "Detailed description",
            "priority": "high|medium|low",
            "category": "efficiency|cost|quality|safety",
            "impact": "Estimated impact",
            "action_items": ["Action 1", "Action 2"]
        }}
    ]
}}

Focus on:
1. Performance improvements
2. Cost reduction
3. Risk mitigation
4. Efficiency gains
5. Quality enhancement
"""
        
        success, response = call_claude_api(user_id, prompt, max_tokens=2000)
        
        if not success:
            return []
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                recommendations = []
                for rec in data.get('recommendations', []):
                    recommendations.append({
                        'text': f"{rec['title']}: {rec['description']}",
                        'priority': rec.get('priority', 'medium'),
                        'category': rec.get('category', 'general'),
                        'full_data': rec
                    })
                return recommendations
        except:
            pass
        
        # Fallback if JSON parsing fails
        return [{
            'text': response[:500],
            'priority': 'medium',
            'category': 'general'
        }]
    
    except Exception as e:
        return [{
            'text': f'Error generating recommendations: {str(e)}',
            'priority': 'low',
            'category': 'error'
        }]

# ============ QUICK INSIGHTS ============
def get_quick_insights(user_id: int, df: pd.DataFrame, column: str) -> str:
    """Get quick insight for a specific column"""
    try:
        data_info = f"""
        Column: {column}
        Type: {df[column].dtype}
        Records: {len(df)}
        Non-null: {df[column].notna().sum()}
        Unique values: {df[column].nunique()}
        
        Statistics:
        {df[column].describe().to_string()}
        
        Provide a brief, insightful analysis of this column's data quality and trends.
        """
        
        success, response = call_claude_api(user_id, data_info)
        return response if success else "Unable to generate insights"
    except:
        return "Error analyzing column"

# ============ NATURAL LANGUAGE CHAT ============
def chat_with_data(user_id: int, df: pd.DataFrame, user_message: str) -> str:
    """Natural language chat about data"""
    try:
        prompt = f"""
You are a data analyst assistant. A user is asking about their data.

Dataset Info:
- Rows: {len(df)}
- Columns: {', '.join(df.columns.tolist())}

Data Sample:
{df.head(10).to_string()}

User Question: {user_message}

Provide a helpful, specific answer based on the data shown.
"""
        
        success, response = call_claude_api(user_id, prompt)
        return response if success else "Unable to process your question"
    except:
        return "Error processing message"

# ============ COMPARISON ANALYSIS ============
def compare_datasets(user_id: int, df1: pd.DataFrame, df2: pd.DataFrame, 
                    label1: str = "Dataset 1", label2: str = "Dataset 2") -> str:
    """Compare two datasets"""
    try:
        prompt = f"""
Compare these two datasets and provide insights:

{label1}:
- Rows: {len(df1)}
- Columns: {len(df1.columns)}
- Summary: {df1.describe().to_string()}

{label2}:
- Rows: {len(df2)}
- Columns: {len(df2.columns)}
- Summary: {df2.describe().to_string()}

Highlight:
1. Key differences
2. Similarities
3. Which dataset performs better
4. Recommendations for improvement
"""
        
        success, response = call_claude_api(user_id, prompt, max_tokens=1500)
        return response if success else "Unable to compare datasets"
    except:
        return "Error comparing datasets"

# ============ ANOMALY EXPLANATION ============
def explain_anomalies(user_id: int, anomalies_df: pd.DataFrame, column: str, 
                     normal_df: pd.DataFrame) -> str:
    """Explain detected anomalies using Claude"""
    try:
        prompt = f"""
Analyze these anomalous records and explain why they might be unusual:

Column being analyzed: {column}

Anomalous Records:
{anomalies_df.to_string()}

Normal data range statistics:
{normal_df[column].describe().to_string()}

Provide:
1. Why these are anomalies
2. Possible causes
3. Whether they need investigation
4. Recommended actions
"""
        
        success, response = call_claude_api(user_id, prompt)
        return response if success else "Unable to explain anomalies"
    except:
        return "Error analyzing anomalies"

# ============ FORECAST EXPLANATION ============
def explain_forecast(user_id: int, forecast_df: pd.DataFrame, column: str, 
                    trend: float, history_data: pd.Series) -> str:
    """Explain forecast using Claude"""
    try:
        trend_direction = "upward" if trend > 0 else "downward"
        trend_strength = abs(trend)
        
        prompt = f"""
Interpret this data forecast:

Column: {column}
Historical Average: {history_data.mean():.2f}
Historical Std Dev: {history_data.std():.2f}
Trend: {trend_direction} ({trend_strength:.2f} per period)

Forecast Data:
{forecast_df.to_string()}

Provide:
1. Trend interpretation
2. Forecast reliability assessment
3. Key drivers of the trend
4. Business implications
5. Recommended actions
"""
        
        success, response = call_claude_api(user_id, prompt)
        return response if success else "Unable to explain forecast"
    except:
        return "Error explaining forecast"

# ============ REPORT GENERATION ============
def generate_ai_report_summary(user_id: int, df: pd.DataFrame, filename: str, 
                             industry: str, analysis_results: Dict) -> str:
    """Generate AI summary for report"""
    try:
        prompt = f"""
Generate an executive summary for a report on {industry} data:

File: {filename}
Records: {len(df)}
Industries: {industry}

Analysis Results:
{json.dumps(analysis_results, indent=2, default=str)}

Data Overview:
{df.describe().to_string()}

Write a 2-3 paragraph executive summary that:
1. Summarizes key findings
2. Highlights major insights
3. Identifies critical issues
4. Recommends next steps
"""
        
        success, response = call_claude_api(user_id, prompt, max_tokens=1000)
        return response if success else "Unable to generate summary"
    except:
        return "Error generating summary"

# ============ HEALTH CHECK ============
def check_api_connection(user_id: int) -> Tuple[bool, str]:
    """Check if Claude API is properly configured"""
    api_key = get_api_key(user_id, 'claude')
    
    if not api_key:
        return False, "❌ No Claude API key configured"
    
    if len(api_key) < 20:
        return False, "❌ API key appears invalid (too short)"
    
    try:
        success, response = call_claude_api(user_id, "Say 'OK' if you can read this.", max_tokens=10)
        if success and "OK" in response:
            return True, "✅ Claude API is working properly"
        else:
            return False, "❌ API key seems invalid"
    except:
        return False, "❌ Unable to connect to Claude API"

# ============ BATCH PROCESSING ============
def analyze_multiple_columns(user_id: int, df: pd.DataFrame, columns: List[str], 
                            industry: str) -> Dict[str, str]:
    """Analyze multiple columns efficiently"""
    results = {}
    
    for col in columns[:5]:  # Limit to 5 columns per batch
        if col in df.columns:
            insight = get_quick_insights(user_id, df, col)
            results[col] = insight
    
    return results
