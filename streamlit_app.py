import streamlit as st

import datetime

from option_pricing import BSMOptionPricing

st.title("Option Pricing App")

st.title('Option pricing')

pricing_method = st.sidebar.radio('Select Pricing Method', options=['BSMf.'])

st.subheader(f'Pricing method: {pricing_method}')

if pricing_method == 'BSMf.':

    option_type = st.radio('Option Type', optiions=['Call', 'Put'])

    stock_price = st.number_input('Stock Price')

    strike_price = st.number_input('Strike Price')

    risk_free_rate = st.slider('Risk-Free Rate (%)', 0, 1, .1)

    sigma = st.slider('Sigma (%)', 0, 1, .1)

    exercise_date = st.date_input('Exercise date', min_value=datetime.today() + datetime.timedelta(days=1), value=datetime.today() + datetime.timedelta(days=365))
    
    if st.button(f'Initate Calculation of Option Price'):

        days_to_maturity = (exercise_date - datetime.now().date()).days

        #initiate BSMf.
        BSM = BSMOptionPricing(
            S = stock_price,
            K = strike_price,
            T = days_to_maturity,
            R = risk_free_rate,
            sigma = sigma
        )

        # Displaying call/put option price
        st.subheader(f'{option_type} option price: {BSM.blackscholes(option_type=option_type)}')
