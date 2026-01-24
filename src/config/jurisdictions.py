"""
Jurisdiction Configuration - Temporal Time-Series Structure
Defines Medicaid Rules with effective dates for supported states.
Supports historical rates for accurate penalty calculations.
"""

from datetime import datetime
from typing import Dict, Any

# =============================================================================
# TEMPORAL MEDICAID RULES (2025-2026)
# =============================================================================

MEDICAID_RULES_TEMPORAL = {
    "PA": {
        "name": "Pennsylvania",
        "lookback_months": 60,
        "divisor_type": "daily",
        "rates": {
            "2025": {
                "divisor": 482.50,
                "effective_date": "2025-01-01",
                "monthly_gift_exemption": 500.00,
                "cash_threshold": 500.00,
                "asset_limit": 2400.00
            },
            "2026": {
                "divisor": 421.20,  # NEW 2026 RATE
                "effective_date": "2026-01-01",
                "monthly_gift_exemption": 500.00,
                "cash_threshold": 500.00,
                "asset_limit": 2400.00
            }
        }
    },
    
    "NY": {
        "name": "New York",
        "lookback_months": 60,
        "divisor_type": "monthly",
        "regional": True,  # FLAG: This state has regional rates
        "regions": {
            "NYC": {
                "name": "New York City",
                "divisor": 14582.00,
                "effective_date": "2025-01-01"
            },
            "Long Island": {
                "name": "Long Island",
                "divisor": 14914.00,
                "effective_date": "2025-01-01"
            },
            "Northern Metropolitan": {
                "name": "Northern Metropolitan",
                "divisor": 14569.00,
                "effective_date": "2025-01-01"
            },
            "Northeastern": {
                "name": "Northeastern",
                "divisor": 13916.00,
                "effective_date": "2025-01-01"
            },
            "Central": {
                "name": "Central",
                "divisor": 13042.00,
                "effective_date": "2025-01-01"
            },
            "Rochester": {
                "name": "Rochester",
                "divisor": 15127.00,
                "effective_date": "2025-01-01"
            },
            "Western": {
                "name": "Western",
                "divisor": 12842.00,
                "effective_date": "2025-01-01"
            }
        },
        "default_region": "NYC",
        "monthly_gift_exemption": 2000.00,
        "cash_threshold": 500.00,
        "asset_limit": 31175.00
    },
    
    "FL": {
        "name": "Florida",
        "lookback_months": 60,
        "divisor_type": "monthly",
        "rates": {
            "2025": {
                "divisor": 10645.00,  # April 2025 rate
                "effective_date": "2025-04-01",
                "monthly_gift_exemption": 1200.00,
                "cash_threshold": 500.00,
                "asset_limit": 2000.00
            }
        }
    },
    
    "CA": {
        "name": "California",
        "lookback_months": 30,  # UNIQUE: 2.5 years only
        "divisor_type": "monthly",
        "rates": {
            "2025": {
                "divisor": 13656.00,
                "effective_date": "2025-01-01",
                "monthly_gift_exemption": 500.00,
                "cash_threshold": 500.00,
                "asset_limit": 130000.00
            }
        }
    },
    
    "TX": {
        "name": "Texas",
        "lookback_months": 60,
        "divisor_type": "daily",
        "rates": {
            "2025": {
                "divisor": 262.37,
                "effective_date": "2025-09-01",  # Sept 1 effective date
                "monthly_gift_exemption": 200.00,
                "cash_threshold": 200.00,
                "asset_limit": 2000.00
            }
        }
    },
    
    "OH": {
        "name": "Ohio",
        "lookback_months": 60,
        "divisor_type": "monthly",
        "rates": {
            "2025": {
                "divisor": 7787.00,
                "effective_date": "2025-01-01",
                "monthly_gift_exemption": 0.00,
                "cash_threshold": 500.00,
                "asset_limit": 2000.00
            }
        }
    },
    
    "NJ": {
        "name": "New Jersey",
        "lookback_months": 60,
        "divisor_type": "daily",
        "rates": {
            "2025": {
                "divisor": 402.74,  # DECREASED from 2024 (punitive!)
                "effective_date": "2025-04-01",
                "monthly_gift_exemption": 500.00,
                "cash_threshold": 500.00,
                "asset_limit": 2000.00
            }
        }
    }
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_effective_divisor(state_code: str, application_date: str = None, region: str = None) -> Dict[str, Any]:
    """
    Get the correct divisor for a given state, date, and optional region.
    
    Args:
        state_code: State abbreviation (e.g., 'PA', 'NY')
        application_date: ISO date string (YYYY-MM-DD). Defaults to today.
        region: For NY, specify region (e.g., 'NYC', 'Long Island')
    
    Returns:
        Dictionary with divisor and metadata
    
    Example:
        >>> get_effective_divisor('PA', '2025-12-31')
        {'divisor': 482.50, 'year': '2025', 'type': 'daily'}
        >>> get_effective_divisor('PA', '2026-01-02')
        {'divisor': 421.20, 'year': '2026', 'type': 'daily'}
    """
    if application_date is None:
        application_date = datetime.now().strftime('%Y-%m-%d')
    
    app_date = datetime.strptime(application_date, '%Y-%m-%d')
    
    rules = MEDICAID_RULES_TEMPORAL.get(state_code)
    if not rules:
        raise ValueError(f"Unknown state code: {state_code}")
    
    # Handle regional states (NY)
    if rules.get('regional'):
        if not region:
            region = rules['default_region']
        
        region_data = rules['regions'].get(region)
        if not region_data:
            raise ValueError(f"Unknown region: {region} for state {state_code}")
        
        return {
            'divisor': region_data['divisor'],
            'type': rules['divisor_type'],
            'region': region,
            'lookback_months': rules['lookback_months'],
            'effective_date': region_data['effective_date']
        }
    
    # Handle temporal rates (PA, FL, etc.)
    if 'rates' in rules:
        # Find the correct year/rate based on effective date
        selected_rate = None
        selected_year = None
        
        for year, rate_data in rules['rates'].items():
            effective_date = datetime.strptime(rate_data['effective_date'], '%Y-%m-%d')
            
            # If application date is >= effective date, this rate applies
            if app_date >= effective_date:
                # Keep the most recent rate that's still valid
                if selected_rate is None or effective_date > datetime.strptime(selected_rate['effective_date'], '%Y-%m-%d'):
                    selected_rate = rate_data
                    selected_year = year
        
        if selected_rate is None:
            # Fallback to oldest rate if app date is before all effective dates
            selected_year = min(rules['rates'].keys())
            selected_rate = rules['rates'][selected_year]
        
        return {
            'divisor': selected_rate['divisor'],
            'type': rules['divisor_type'],
            'year': selected_year,
            'lookback_months': rules['lookback_months'],
            'effective_date': selected_rate['effective_date'],
            'monthly_gift_exemption': selected_rate.get('monthly_gift_exemption', 0),
            'cash_threshold': selected_rate.get('cash_threshold', 500),
            'asset_limit': selected_rate.get('asset_limit', 2000)
        }
    
    raise ValueError(f"No rate data found for {state_code}")


def get_ny_regions() -> list:
    """Returns list of NY region names for UI dropdown"""
    return list(MEDICAID_RULES_TEMPORAL['NY']['regions'].keys())


# =============================================================================
# BACKWARD COMPATIBILITY (Legacy MEDICAID_RULES)
# =============================================================================

def get_legacy_rules(state_code: str, region: str = None) -> Dict[str, Any]:
    """
    Provides backward-compatible MEDICAID_RULES format.
    Uses current date to select appropriate rate.
    """
    divisor_data = get_effective_divisor(state_code, region=region)
    rules = MEDICAID_RULES_TEMPORAL[state_code]
    
    # For regional states, use region-specific data
    if rules.get('regional'):
        return {
            'name': f"{rules['name']} ({divisor_data['region']} Region)",
            'divisor': divisor_data['divisor'],
            'lookback_months': divisor_data['lookback_months'],
            'monthly_gift_exemption': rules['monthly_gift_exemption'],
            'cash_threshold': rules['cash_threshold'],
            'asset_limit': rules['asset_limit']
        }
    
    # For temporal states, merge with selected rate
    return {
        'name': f"{rules['name']} ({divisor_data['year']})",
        'divisor': divisor_data['divisor'],
        'lookback_months': divisor_data['lookback_months'],
        'monthly_gift_exemption': divisor_data.get('monthly_gift_exemption', 0),
        'cash_threshold': divisor_data.get('cash_threshold', 500),
        'asset_limit': divisor_data.get('asset_limit', 2000)
    }


# Maintain legacy MEDICAID_RULES for existing code
MEDICAID_RULES = {
    state: get_legacy_rules(state) 
    for state in MEDICAID_RULES_TEMPORAL.keys()
}
