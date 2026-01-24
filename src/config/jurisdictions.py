"""
Jurisdiction Configuration
Defines 2026 Medicaid Rules for supported states.
"""

MEDICAID_RULES = {
    "PA": {
        "name": "Pennsylvania (2026)",
        "divisor": 482.50, 
        "lookback_months": 60,
        "monthly_gift_exemption": 500.00,
        "cash_threshold": 500.00,
        "asset_limit": 2400.00
    },
    "NY": {
        "name": "New York (NYC Region)",
        "divisor": 15150.00, 
        "lookback_months": 60,
        "monthly_gift_exemption": 2000.00, 
        "cash_threshold": 500.00,
        "asset_limit": 31175.00
    },
    "FL": {
        "name": "Florida",
        "divisor": 10809.00,
        "lookback_months": 60,
        "monthly_gift_exemption": 1200.00,
        "cash_threshold": 500.00,
        "asset_limit": 2000.00
    },
    "CA": {
        "name": "California",
        "divisor": 11576.00,
        "lookback_months": 30,
        "monthly_gift_exemption": 500.00,
        "cash_threshold": 500.00,
        "asset_limit": 130000.00
    },
    "TX": {
        "name": "Texas",
        "divisor": 242.60, # Daily
        "lookback_months": 60,
        "monthly_gift_exemption": 200.00,
        "cash_threshold": 200.00,
        "asset_limit": 2000.00
    },
    "OH": {
         "name": "Ohio",
         "divisor": 7453.00,
         "lookback_months": 60,
         "monthly_gift_exemption": 0.00,
         "cash_threshold": 500.00,
         "asset_limit": 2000.00
    },
    "NJ": {
         "name": "New Jersey",
         "divisor": 14785.00,
         "lookback_months": 60,
         "monthly_gift_exemption": 500.00,
         "cash_threshold": 500.00,
         "asset_limit": 2000.00
    }
}
