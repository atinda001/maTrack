import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.passengers_file = "data/passengers.csv"
        self.expenses_file = "data/expenses.csv"
        self._initialize_files()

    def _initialize_files(self):
        """Initialize CSV files if they don't exist"""
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.passengers_file):
            pd.DataFrame(columns=[
                'name', 'phone', 'origin', 'destination', 'fare', 'journey_date'
            ]).to_csv(self.passengers_file, index=False)

        if not os.path.exists(self.expenses_file):
            pd.DataFrame(columns=[
                'expense_type', 'amount', 'date', 'notes'
            ]).to_csv(self.expenses_file, index=False)

    def add_passenger_journey(self, name, phone, origin, destination, fare, journey_date):
        """Add a new passenger journey"""
        journey = pd.DataFrame([[name, phone, origin, destination, fare, journey_date]], 
                             columns=['name', 'phone', 'origin', 'destination', 'fare', 'journey_date'])
        journey.to_csv(self.passengers_file, mode='a', header=False, index=False)

    def get_passenger_journeys(self):
        """Get all passenger journeys"""
        return pd.read_csv(self.passengers_file)

    def add_expense(self, expense_type, amount, date, notes):
        """Add a new expense"""
        expense = pd.DataFrame([[expense_type, amount, date, notes]], 
                             columns=['expense_type', 'amount', 'date', 'notes'])
        expense.to_csv(self.expenses_file, mode='a', header=False, index=False)

    def get_expenses(self):
        """Get all expenses"""
        return pd.read_csv(self.expenses_file)

    def get_daily_revenue(self, start_date, end_date):
        """Get daily revenue between dates"""
        journeys = pd.read_csv(self.passengers_file)
        journeys['journey_date'] = pd.to_datetime(journeys['journey_date'])
        mask = (journeys['journey_date'] >= pd.Timestamp(start_date)) & \
               (journeys['journey_date'] <= pd.Timestamp(end_date))
        daily = journeys[mask].groupby('journey_date')['fare'].sum().reset_index()
        daily.columns = ['date', 'revenue']
        return daily

    def get_expense_breakdown(self, start_date, end_date):
        """Get expense breakdown between dates"""
        expenses = pd.read_csv(self.expenses_file)
        expenses['date'] = pd.to_datetime(expenses['date'])
        mask = (expenses['date'] >= pd.Timestamp(start_date)) & \
               (expenses['date'] <= pd.Timestamp(end_date))
        return expenses[mask].groupby('expense_type')['amount'].sum().reset_index()