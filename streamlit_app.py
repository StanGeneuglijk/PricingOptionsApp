import streamlit as st
import datetime
from option_pricing.pricing import BSMOptionPricing

st.title("Option Pricing App")

pricing_method = st.sidebar.radio('Select Pricing Method', options=['BSM'])

st.subheader(f'Pricing method: {pricing_method}')

if pricing_method == 'BSM':
    option_type = st.radio('Option Type', options=['Call', 'Put'])

    stock_price = st.number_input('Stock Price', min_value=0.0, step=1.0)

    strike_price = st.number_input('Strike Price', min_value=0.0, step=1.0)

    risk_free_rate = st.slider('Risk-Free Rate (%)', 0.0, 10.0, 0.1) / 100  

    sigma = st.slider('Sigma (%)', 0.0, 100.0, 1.0) / 100

    exercise_date = st.date_input('Exercise date', min_value=datetime.datetime.today() + datetime.timedelta(days=1), value=datetime.datetime.today() + datetime.timedelta(days=365))
    
    if st.button('Initiate Calculation of Option Price'):
        days_to_maturity = (exercise_date - datetime.datetime.now().date()).days

        # Initiate BSM
        BSM = BSMOptionPricing(
            S=stock_price,
            K=strike_price,
            T=days_to_maturity / 365,
            R=risk_free_rate,
            sigma=sigma
        )

        # Displaying call/put option price
        st.subheader(f'{option_type} option price: {BSM.blackscholes(option_type=option_type)}')
