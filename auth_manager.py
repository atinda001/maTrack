import streamlit as st
import streamlit_authenticator as stauth
import bcrypt
from database import SessionLocal, User
from google.oauth2 import id_token
from google.auth.transport import requests
import os

class AuthManager:
    def __init__(self):
        self.db = SessionLocal()
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def register_user(self, email, password, name):
        try:
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                return False, "Email already registered"

            hashed_password = self.hash_password(password)
            new_user = User(
                email=email,
                password_hash=hashed_password,
                name=name,
                is_google_auth=False
            )
            self.db.add(new_user)
            self.db.commit()
            return True, "Registration successful"
        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def login_user(self, email, password):
        try:
            user = self.db.query(User).filter(User.email == email).first()
            if user and not user.is_google_auth and self.verify_password(password, user.password_hash):
                st.session_state.authenticated = True
                st.session_state.user_id = user.id
                return True, "Login successful"
            return False, "Invalid email or password"
        except Exception as e:
            return False, str(e)

    def google_auth_callback(self, token):
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
            
            email = idinfo['email']
            user = self.db.query(User).filter(User.email == email).first()
            
            if not user:
                user = User(
                    email=email,
                    name=idinfo.get('name'),
                    is_google_auth=True,
                    google_id=idinfo['sub']
                )
                self.db.add(user)
                self.db.commit()
            
            st.session_state.authenticated = True
            st.session_state.user_id = user.id
            return True, "Google login successful"
        except Exception as e:
            return False, str(e)

    def logout_user(self):
        st.session_state.authenticated = False
        st.session_state.user_id = None

    def __del__(self):
        self.db.close()
