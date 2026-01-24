"""
Keyword highlighting utilities for AI transparency.
Highlights trigger words that caused AI to flag transactions.
"""

def highlight_keywords(description: str, risk_level: str) -> str:
    """
    Highlight keywords in transaction description based on risk level.
    
    Args:
        description: Transaction description text
        risk_level: Risk classification (High/Medium/Low)
    
    Returns:
        HTML string with highlighted keywords
    """
    if not description or not risk_level:
        return str(description)
    
    # Risk-specific keywords
    RISK_KEYWORDS = {
        'High': [
            'gift', 'donation', 'charity', 'charitable',
            'zelle', 'venmo', 'cash app', 'paypal',
            'transfer to', 'wire', 'atm withdrawal',
            'casino', 'lottery', 'gambling',
            'family member', 'relative', 'friend'
        ],
        'Medium': [
            'cash', 'withdrawal', 'atm',
            'transfer', 'payment',
            'check', 'debit',
            'unusual', 'large'
        ]
    }
    
    keywords = RISK_KEYWORDS.get(risk_level, [])
    
    # Highlight matching keywords
    highlighted = description
    for keyword in keywords:
        # Case-insensitive replacement
        import re
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        
        # Replace with highlighted version
        def replacer(match):
            return f'<mark style="background: #FFF4E6; color: #D97706; padding: 2px 4px; border-radius: 3px; font-weight: 500;">{match.group()}</mark>'
        
        highlighted = pattern.sub(replacer, highlighted)
    
    return highlighted


def get_confidence_badge(confidence: int) -> str:
    """
    Generate HTML badge for confidence score.
    
    Args:
        confidence: Confidence percentage (0-100)
    
    Returns:
        HTML string with styled badge
    """
    # Color coding based on confidence level
    if confidence >= 90:
        bg_color = 'rgba(5, 150, 105, 0.1)'  # Green
        text_color = '#059669'
        icon = '✓'
    elif confidence >= 70:
        bg_color = 'rgba(217, 119, 6, 0.1)'  # Amber
        text_color = '#D97706'
        icon = '~'
    else:
        bg_color = 'rgba(220, 38, 38, 0.1)'  # Red
        text_color = '#DC2626'
        icon = '!'
    
    return f"""
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 600;
        color: {text_color};
        background: {bg_color};
        padding: 3px 8px;
        border-radius: 4px;
        font-family: 'Inter', sans-serif;
    " title="AI Confidence: {confidence}%">
        <span>{icon}</span>
        <span>{confidence}%</span>
    </span>
    """
