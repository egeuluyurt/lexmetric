"""
Regulatory Truth Configuration
Defines state-specific rules for Medicaid penalty calculations (2026).
"""

REGULATORY_DATA_2026 = {
    "PA": {
        "daily_penalty_divisor": 482.50, 
        "asset_limit": 2400.00,
        "region_name": "Pennsylvania Standard"
    },
    "FL": {
        "daily_penalty_divisor": 375.00, 
        "asset_limit": 2000.00,
        "region_name": "Florida Statewide"
    },
    "NY": {
        "daily_penalty_divisor": 515.00, # Estimated average for Northern Region / NYC varies
        "asset_limit": 31175.00, # 2025 limit was ~30k, 2026 est.
        "region_name": "New York Regional Average"
    },
    "CA": {
        "daily_penalty_divisor": 390.00, 
        "asset_limit": 130000.00,  # CA asset limits have been effectively eliminated/raised significantly
        "region_name": "California Statewide"
    }
}
