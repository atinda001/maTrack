import pandas as pd
from datetime import datetime, timedelta
from database import SessionLocal, Passenger, Journey, Expense
from sqlalchemy import func, extract

class DataManager:
    def __init__(self):
        self.db = SessionLocal()

    def add_passenger_journey(self, name, phone, origin, destination, fare, journey_date):
        """Add a new passenger journey"""
        try:
            # Check if passenger exists
            passenger = self.db.query(Passenger).filter_by(phone=phone).first()
            if not passenger:
                passenger = Passenger(
                    name=name,
                    phone=phone,
                    owner_id=st.session_state.user_id
                )
                self.db.add(passenger)
                self.db.flush()

            # Create journey
            journey = Journey(
                passenger_id=passenger.id,
                origin=origin,
                destination=destination,
                fare=fare,
                journey_date=journey_date
            )
            self.db.add(journey)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error adding passenger journey: {str(e)}")

    def get_passenger_journeys(self):
        """Get all passenger journeys for the current user"""
        try:
            journeys = self.db.query(
                Journey.journey_date,
                Passenger.name,
                Passenger.phone,
                Journey.origin,
                Journey.destination,
                Journey.fare
            ).join(Passenger).filter(
                Passenger.owner_id == st.session_state.user_id
            ).all()

            return pd.DataFrame([{
                'journey_date': j.journey_date,
                'name': j.name,
                'phone': j.phone,
                'origin': j.origin,
                'destination': j.destination,
                'fare': j.fare
            } for j in journeys])
        except Exception as e:
            raise Exception(f"Error reading passenger journeys: {str(e)}")

    def add_expense(self, expense_type, amount, date, notes):
        """Add a new expense"""
        try:
            expense = Expense(
                expense_type=expense_type,
                amount=amount,
                date=date,
                notes=notes,
                owner_id=st.session_state.user_id
            )
            self.db.add(expense)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error adding expense: {str(e)}")

    def get_expenses(self):
        """Get all expenses for the current user"""
        try:
            expenses = self.db.query(Expense).filter(
                Expense.owner_id == st.session_state.user_id
            ).all()
            return pd.DataFrame([{
                'expense_type': e.expense_type,
                'amount': e.amount,
                'date': e.date,
                'notes': e.notes
            } for e in expenses])
        except Exception as e:
            raise Exception(f"Error reading expenses: {str(e)}")

    def get_revenue_by_period(self, start_date, end_date, period_type):
        """Get revenue analysis by period (Weekly/Monthly)"""
        try:
            query = self.db.query(
                func.date_trunc(
                    'week' if period_type == 'Weekly' else 'month',
                    Journey.journey_date
                ).label('period'),
                func.sum(Journey.fare).label('revenue')
            ).join(Passenger).filter(
                Journey.journey_date.between(start_date, end_date),
                Passenger.owner_id == st.session_state.user_id
            ).group_by('period').order_by('period')

            results = query.all()

            return pd.DataFrame([{
                'period': r.period,
                'revenue': r.revenue
            } for r in results])
        except Exception as e:
            raise Exception(f"Error calculating revenue by period: {str(e)}")

    def get_performance_metrics(self, start_date, end_date, period_type):
        """Get performance metrics for the selected period"""
        try:
            # Get journey metrics
            journeys = self.db.query(Journey).join(Passenger).filter(
                Journey.journey_date.between(start_date, end_date),
                Passenger.owner_id == st.session_state.user_id
            ).all()

            # Get expense metrics
            expenses = self.db.query(Expense).filter(
                Expense.date.between(start_date, end_date),
                Expense.owner_id == st.session_state.user_id
            ).all()

            if not journeys:
                return None

            # Calculate metrics
            total_trips = len(set(j.journey_date for j in journeys))
            total_passengers = len(journeys)
            total_revenue = sum(j.fare for j in journeys)
            total_expenses = sum(e.amount for e in expenses)

            return {
                'Total Trips': total_trips,
                'Total Passengers': total_passengers,
                'Average Passengers per Trip': round(total_passengers / total_trips if total_trips > 0 else 0, 2),
                'Average Revenue per Trip': round(total_revenue / total_trips if total_trips > 0 else 0, 2),
                'Total Expenses': total_expenses
            }
        except Exception as e:
            raise Exception(f"Error calculating performance metrics: {str(e)}")

    def get_expense_breakdown(self, start_date, end_date):
        """Get expense breakdown between dates"""
        try:
            expenses = self.db.query(
                Expense.expense_type,
                func.sum(Expense.amount).label('amount')
            ).filter(
                Expense.date.between(start_date, end_date),
                Expense.owner_id == st.session_state.user_id
            ).group_by(Expense.expense_type).all()

            return pd.DataFrame([{
                'expense_type': e.expense_type,
                'amount': e.amount
            } for e in expenses])
        except Exception as e:
            raise Exception(f"Error calculating expense breakdown: {str(e)}")

    def __del__(self):
        """Close the database session"""
        self.db.close()