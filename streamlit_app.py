import streamlit as st
import datetime
import matplotlib.pyplot as plt
from option_pricing.pricing import BSMOptionPricing, MertonJumpOptionPricing
from option_pricing.simulation import MCOptionPricing, MCJumpOptionPricing

# Set up the page navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page:", ["Black-Scholes", "Merton Jump-Diffusion"])

# Common input parameters
st.sidebar.subheader("Common Parameters")
option_type = st.sidebar.radio('Option Type', options=['Call', 'Put'])
stock_price = st.sidebar.number_input('Stock Price', min_value=0.0, step=1.0)
strike_price = st.sidebar.number_input('Strike Price', min_value=0.0, step=1.0)
risk_free_rate = st.sidebar.slider('Risk-Free Rate (%)', 0.0, 10.0, 0.1) / 100  
exercise_date = st.sidebar.date_input('Exercise Date', min_value=datetime.datetime.today() + datetime.timedelta(days=1), value=datetime.datetime.today() + datetime.timedelta(days=365))

# Calculate the time to maturity in years
days_to_maturity = (exercise_date - datetime.datetime.now().date()).days
T = days_to_maturity / 365

# Black-Scholes Page
if page == "Black-Scholes":
    st.title("Black-Scholes Option Pricing")
    use_simulation = st.checkbox("Use Monte Carlo Simulation")

    sigma = st.slider('Sigma (%)', 0.0, 100.0, 1.0) / 100

    if not use_simulation:
        if st.button('Calculate Option Price (Theoretical)'):
            BSM = BSMOptionPricing(
                S=stock_price,
                K=strike_price,
                T=T,
                R=risk_free_rate,
                sigma=sigma
            )
            option_price = BSM.black_scholes(option_type=option_type)
            st.write(f'Option price (Theoretical BSM): {round(option_price, 3)}')
    else:
        intervals = st.slider('Number of Intervals', min_value=10, max_value=500, value=252)
        simulations = st.slider('Number of Simulations', min_value=100, max_value=10000, value=1000)

        if st.button('Run Monte Carlo Simulation'):
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
            st.write(f'Simulated Option Price (BSM): {round(option_price, 3)}')

            st.write("Simulated Asset Price Paths:")
            fig, ax = plt.subplots()
            mc_model.plot_simulated_paths(num_paths_to_plot=10)
            st.pyplot(fig)

# Merton Jump-Diffusion Page
elif page == "Merton Jump-Diffusion":
    st.title("Merton Jump-Diffusion Option Pricing")
    use_simulation = st.checkbox("Use Monte Carlo Simulation")

    sigma = st.slider('Sigma (%)', 0.0, 100.0, 1.0) / 100
    jump_intensity = st.slider('Jump Intensity (λ)', 0.0, 2.0, 0.1)
    jump_mean = st.slider('Jump Mean (μ)', -2.0, 2.0, 0.0)
    jump_volatility = st.slider('Jump Volatility (σ_jump)', 0.0, 100.0, 1.0) / 100

    if not use_simulation:
        if st.button('Calculate Option Price (Theoretical)'):
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
            st.write(f'Option price (Theoretical Merton): {round(option_price, 3)}')
    else:
        intervals = st.slider('Number of Intervals', min_value=10, max_value=500, value=252)
        simulations = st.slider('Number of Simulations', min_value=100, max_value=10000, value=1000)

        if st.button('Run Monte Carlo Simulation'):
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
            st.write(f'Simulated Option Price (Merton Jump-Diffusion): {round(option_price, 3)}')

            st.write("Simulated Asset Price Paths:")
            fig, ax = plt.subplots()
            mc_jump_model.plot_simulated_paths(num_paths_to_plot=10)
            st.pyplot(fig)
