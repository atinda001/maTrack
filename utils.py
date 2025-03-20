import re
import pandas as pd

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def calculate_financial_metrics(data_manager, start_date, end_date):
    """Calculate financial metrics between dates"""
    # Get journeys and expenses
    journeys = data_manager.get_passenger_journeys()
    expenses = data_manager.get_expenses()
    
    # Convert dates
    journeys['journey_date'] = pd.to_datetime(journeys['journey_date'])
    expenses['date'] = pd.to_datetime(expenses['date'])
    
    # Filter by date range
    journey_mask = (journeys['journey_date'] >= pd.Timestamp(start_date)) & \
                  (journeys['journey_date'] <= pd.Timestamp(end_date))
    expense_mask = (expenses['date'] >= pd.Timestamp(start_date)) & \
                  (expenses['date'] <= pd.Timestamp(end_date))
    
    # Calculate metrics
    total_revenue = journeys[journey_mask]['fare'].sum()
    total_expenses = expenses[expense_mask]['amount'].sum()
    net_profit = total_revenue - total_expenses
    
    return {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit
    }
