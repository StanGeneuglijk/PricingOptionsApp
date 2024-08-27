import streamlit as st
import datetime
import matplotlib.pyplot as plt
from option_pricing.pricing import BSMOptionPricing, MertonJumpOptionPricing
from option_pricing.simulation import MCOptionPricing, MCJumpOptionPricing

st.title("Option Pricing App")

# Add BSM, Merton Jump-Diffusion, and Simulation to the pricing methods
pricing_method = st.sidebar.radio('Select Pricing Method', options=['BSM', 'Merton Jump-Diffusion', 'Monte Carlo Simulation'])

st.subheader(f'Pricing method: {pricing_method}')

# Common inputs for both methods
option_type = st.radio('Option Type', options=['Call', 'Put'])
stock_price = st.number_input('Stock Price', min_value=0.0, step=1.0)
strike_price = st.number_input('Strike Price', min_value=0.0, step=1.0)
risk_free_rate = st.slider('Risk-Free Rate (%)', 0.0, 10.0, 0.1) / 100  
exercise_date = st.date_input('Exercise date', min_value=datetime.datetime.today() + datetime.timedelta(days=1), value=datetime.datetime.today() + datetime.timedelta(days=365))

# Calculate the time to maturity in years
days_to_maturity = (exercise_date - datetime.datetime.now().date()).days
T = days_to_maturity / 365

if pricing_method == 'BSM':
    sigma = st.slider('Sigma (%)', 0.0, 100.0, 5.0) / 100

    if st.button('Calculate Option Price'):
        BSM = BSMOptionPricing(
            S=stock_price,
            K=strike_price,
            T=T,
            R=risk_free_rate,
            sigma=sigma
        )
        option_price = BSM.black_scholes(option_type=option_type)
        st.write(f'Option price (BSM): {round(option_price, 3)}')

elif pricing_method == 'Merton Jump-Diffusion':
    sigma = st.slider('Sigma (%)', 0.0, 100.0, 5.0) / 100
    jump_intensity = st.slider('Jump Intensity (λ)', 0.0, 2.0, 0.5)
    jump_mean = st.slider('Jump Mean (μ)', -2.0, 2.0, 0.5)
    jump_volatility = st.slider('Jump Volatility (σ_jump)', 0.0, 100.0, 5.0) / 100

    if st.button('Calculate Option Price'):
        Merton = MertonJumpOptionPricing(
            S=stock_price,
            K=strike_price,
            T=T,
            R=risk_free_rate,
            sigma=sigma,
            lambda_=jump_intensity,
            mu_jump=jump_mean,
            sigma_jump=jump_volatility
        )
        option_price = Merton.merton_jump_diffusion(option_type=option_type)
        st.write(f'Option price (Merton Jump-Diffusion): {round(option_price, 3)}')

elif pricing_method == 'Monte Carlo Simulation':
    sigma = st.slider('Sigma (%)', 0.0, 100.0, 1.0) / 100
    intervals = st.slider('Number of Intervals', min_value=10, max_value=500, value=252)
    simulations = st.slider('Number of Simulations', min_value=100, max_value=10000, value=1000)

    if st.checkbox('Use Jump-Diffusion Model'):
        jump_intensity = st.slider('Jump Intensity (λ)', 0.0, 2.0, 0.1)
        jump_mean = st.slider('Jump Mean (μ)', -2.0, 2.0, 0.0)
        jump_volatility = st.slider('Jump Volatility (σ_jump)', 0.0, 100.0, 1.0) / 100

        if st.button('Run Simulation'):
            mc_jump_model = MCJumpOptionPricing(
                S0=stock_price,
                K=strike_price,
                T=T,
                R=risk_free_rate,
                sigma=sigma,
                intervals=intervals,
                simulations=simulations,
                lambda_=jump_intensity,
                mu_jump=jump_mean,
                sigma_jump=jump_volatility
            )
            option_price = mc_jump_model.pricing(option_type=option_type.lower())
            st.write(f'Simulated Option Price (Jump-Diffusion): {round(option_price, 3)}')

            st.write("Simulated Asset Price Paths:")
            fig, ax = plt.subplots()
            mc_jump_model.plot_simulated_paths(num_paths_to_plot=10)
            st.pyplot(fig)

    else:
        if st.button('Run Simulation'):
            mc_model = MCOptionPricing(
                S0=stock_price,
                K=strike_price,
                T=T,
                R=risk_free_rate,
                sigma=sigma,
                intervals=intervals,
                simulations=simulations
            )
            option_price = mc_model.pricing(option_type=option_type.lower())
            st.write(f'Simulated Option Price: {round(option_price, 3)}')

            st.write("Simulated Asset Price Paths:")
            fig, ax = plt.subplots()
            mc_model.plot_simulated_paths(num_paths_to_plot=10)
            st.pyplot(fig)
