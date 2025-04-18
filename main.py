import streamlit as st
import os
import sys

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import views
from frontend.auth import render_login_view, render_logout_button
from frontend.recommendations import render_recommendations_view
from frontend.dashboard import render_dashboard_view

# Set page config
st.set_page_config(
    page_title="AI Habit Tracker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    footer {visibility: hidden;}
    .stButton button {
        width: 100%;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    /* For better accessibility */
    .streamlit-expanderHeader {
        font-size: 1.2rem;
    }
    /* For high contrast mode support */
    @media (prefers-contrast: high) {
        body {
            background-color: white !important;
            color: black !important;
        }
        .stButton button {
            background-color: #0078D7 !important;
            color: white !important;
            border: 2px solid black !important;
        }
        .stCheckbox > div > div > label {
            color: black !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main function to run the app."""
    # Initialize session state variables if they don't exist
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'view' not in st.session_state:
        st.session_state.view = "login"
    
    # Sidebar for navigation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/goal--v1.png", width=100)
        st.title("AI Habit Tracker")
        
        # Only show navigation if authenticated
        if st.session_state.authenticated:
            st.subheader("Navigation")
            
            if st.button("Dashboard", use_container_width=True):
                st.session_state.view = "dashboard"
                st.rerun()
            
            if st.button("Add Habits", use_container_width=True):
                st.session_state.view = "recommendations"
                st.rerun()
            
            # Add a divider
            st.markdown("---")
            
            # Display user info if available
            if 'user_name' in st.session_state:
                st.markdown(f"Logged in as: **{st.session_state.user_name}**")
            
            # Logout button
            render_logout_button()
        
        # Footer
        st.markdown("---")
        st.caption("© 2023 AI Habit Tracker")
        st.caption("AI-powered habit tracking for better living")
    
    # Main content - render different views based on session state
    if not st.session_state.authenticated:
        render_login_view()
    elif st.session_state.view == "dashboard":
        render_dashboard_view()
    elif st.session_state.view == "recommendations":
        render_recommendations_view()
    else:
        st.error("Unknown view")
        st.session_state.view = "login"
        st.rerun()

if __name__ == "__main__":
    main()
