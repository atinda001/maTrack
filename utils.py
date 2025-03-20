import re
import pandas as pd
from datetime import datetime, timedelta

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def calculate_financial_metrics(data_manager, start_date, end_date, analysis_type='Trip-based'):
    """Calculate financial metrics between dates"""
    try:
        # Get journeys and expenses
        journeys = data_manager.get_passenger_journeys()
        expenses = data_manager.get_expenses()

        # Convert dates
        journeys['journey_date'] = pd.to_datetime(journeys['journey_date'])
        expenses['date'] = pd.to_datetime(expenses['date'])

        # Filter by date range
        journey_mask = (journeys['journey_date'].dt.date >= start_date) & \
                      (journeys['journey_date'].dt.date <= end_date)
        expense_mask = (expenses['date'].dt.date >= start_date) & \
                      (expenses['date'].dt.date <= end_date)

        # Calculate metrics
        filtered_journeys = journeys[journey_mask]
        filtered_expenses = expenses[expense_mask]

        total_revenue = filtered_journeys['fare'].sum()
        total_expenses = filtered_expenses['amount'].sum()
        net_profit = total_revenue - total_expenses

        metrics = {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit
        }

        # Add passenger count for trip-based analysis
        if analysis_type == 'Trip-based':
            metrics['passenger_count'] = len(filtered_journeys)

        return metrics
    except Exception as e:
        print(f"Error calculating financial metrics: {str(e)}")
        return {
            'total_revenue': 0,
            'total_expenses': 0,
            'net_profit': 0,
            'passenger_count': 0
        }