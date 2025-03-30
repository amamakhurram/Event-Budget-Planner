import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Event Budget Planner", layout="wide")

st.markdown(
    """
    <style>
        .main { background-color: #f4f4f4; }
        h1, h2, h3 { color: #2E3B55; text-align: center; }
        .stButton > button { background-color: #4CAF50; color: white; font-size: 16px; }
        .stSelectbox, .stSlider, .stTextInput { margin-bottom: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Budget Entry", "Summary & Analysis"])


template_options = {
    "Wedding": ["Venue", "Catering", "Photography", "Entertainment"],
    "Birthday Party": ["Cake", "Decorations", "Food & Drinks", "Gifts"],
    "Corporate Event": ["Venue", "Speakers", "Refreshments", "Marketing"],
    "Conference": ["Venue", "Speakers", "Catering", "Logistics"],
    "Fundraiser": ["Venue", "Marketing", "Entertainment", "Donations Handling"]
}

try:
    template_choice = st.sidebar.selectbox("Choose a Budget Template", list(template_options.keys()))
    expense_categories = template_options[template_choice]

    if page == "Home":
        st.title("🎉 Event Budget Planner")  

        st.markdown("Plan your event budget efficiently with pre-designed templates and real-time calculations.")
        st.markdown("### How It Works:")
        st.write("1. Choose an event type from the sidebar.")
        st.write("2. Enter your estimated and actual expenses using sliders.")
        st.write("3. Add custom expenses if needed.")
        st.write("4. View a breakdown of your budget and download the report.")

    elif page == "Budget Entry":
        st.title("Budget Entry")
        event_name = st.text_input("Event Name", "My Event")
        st.session_state["event_name"] = event_name
        event_budget = st.slider("Total Budget (PKR)", min_value=100, max_value=100000, value=0, step=500)
        
        st.subheader("Enter Expense Details")
        expense_data = []
        for category in expense_categories:
            estimated_cost = st.slider(f"Estimated Cost for {category} (PKR)", min_value=0, max_value=10000, value=100, step=100)
            actual_cost = st.slider(f"Actual Cost for {category} (PKR)", min_value=0, max_value=10000, value=100, step=100)
            expense_data.append([category, estimated_cost, actual_cost])
        
        
        st.subheader("Add Custom Expenses")
        if "custom_expenses" not in st.session_state:
            st.session_state["custom_expenses"] = []
        
        custom_category = st.text_input("Custom Expense Category")
        custom_estimated = st.slider("Estimated Cost for Custom Expense (PKR)", min_value=0, max_value=10000, value=100, step=100)
        custom_actual = st.slider("Actual Cost for Custom Expense (PKR)", min_value=0, max_value=10000, value=100, step=100)
        
        if st.button("Add Custom Expense"):
            if custom_category:
                st.session_state["custom_expenses"].append([custom_category, custom_estimated, custom_actual])
        
        for custom in st.session_state["custom_expenses"]:
            expense_data.append(custom)
        
        df = pd.DataFrame(expense_data, columns=["Category", "Estimated Cost (PKR)", "Actual Cost (PKR)"])
        st.session_state["df"] = df

    elif page == "Summary & Analysis":
        st.title("Budget Summary & Analysis")
        
        if "df" in st.session_state:
            df = st.session_state["df"]
            df["Difference (PKR)"] = df["Actual Cost (PKR)"] - df["Estimated Cost (PKR)"]
            total_estimated = df["Estimated Cost (PKR)"].sum()
            total_actual = df["Actual Cost (PKR)"].sum()

            st.write(df)
            st.write(f"**Total Estimated Cost:** PKR {total_estimated}")
            st.write(f"**Total Actual Cost:** PKR {total_actual}")

            difference = total_actual - total_estimated
            if difference > 0:
                st.error(f"You overspent by PKR {difference}!")
            elif difference < 0:
                st.success(f"You saved PKR {abs(difference)}!")
            else:
                st.info("Your actual expenses matched your estimated budget!")
            
            # Pie Chart for Expense Breakdown
            st.subheader("Expense Breakdown")
            try:
                fig, ax = plt.subplots()
                ax.pie(df["Actual Cost (PKR)"], labels=df["Category"], autopct='%1.1f%%', startangle=140)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generating pie chart: {e}")
            
            # CSV Export
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            csv_data = convert_df_to_csv(df)
            event_name = st.session_state.get("event_name", "Event")
            st.download_button("Download Budget Report (CSV)", data=csv_data, file_name=f"{event_name}_budget.csv", mime="text/csv")
        else:
            st.warning("Please enter your budget details first in the Budget Entry section.")

except Exception as e:
    st.error(f"An error occurred: {e}")
