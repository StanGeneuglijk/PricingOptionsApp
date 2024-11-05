import streamlit as st
import datetime
import numpy as np
from option_pricing.pricing import BSMOptionPricing, MertonJumpOptionPricing
from option_pricing.simulation import MCOptionPricing, MCJumpOptionPricing
import matplotlib.pyplot as plt

st.set_page_config(page_title="Option Pricing Models", layout="wide")

st.sidebar.title("Option Pricing Models")

page = st.sidebar.radio(
    "Choose a Model:", ["Black-Scholes-Merton", "Merton Jump-Diffusion"]
)

st.sidebar.header("Option Parameters")

option_type = st.sidebar.selectbox(
    "Option Type:",
    ["Call", "Put"],
    help="Select 'Call' for a call option or 'Put' for a put option.",
)

stock_price = st.sidebar.number_input(
    "Current Stock Price (S₀):",
    min_value=0.0,
    step=1.0,
    value=100.0,
    help="The current price of the underlying asset.",
)

strike_price = st.sidebar.number_input(
    "Strike Price (K):",
    min_value=0.0,
    step=1.0,
    value=100.0,
    help="The strike price of the option.",
)

risk_free_rate = (
    st.sidebar.slider(
        "Risk-Free Interest Rate (r) [%]:",
        min_value=0.0,
        max_value=10.0,
        step=0.1,
        value=5.0,
        help="The annual risk-free interest rate, as a percentage.",
    )
    / 100
)

sigma = (
    st.sidebar.slider(
        "Volatility (σ) [%]:",
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        value=20.0,
        help="The volatility of the underlying asset, as a percentage.",
    )
    / 100
)

if page == "Merton Jump-Diffusion":
    st.sidebar.header("Jump Parameters")
    jump_intensity = st.sidebar.slider(
        "Jump Intensity (λ):",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        value=0.1,
        help="Average number of jumps per year.",
    )

    jump_mean = st.sidebar.slider(
        "Jump Mean (μj):",
        min_value=-0.5,
        max_value=0.5,
        step=0.01,
        value=0.0,
        help="Mean of the logarithm of the jump size.",
    )

    jump_volatility = (
        st.sidebar.slider(
            "Jump Volatility (σj) [%]:",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            value=20.0,
            help="Volatility of the jump size, as a percentage.",
        )
        / 100
    )

st.sidebar.header("Expiration")
exercise_date = st.sidebar.date_input(
    "Exercise Date (T):",
    min_value=datetime.date.today(),
    value=datetime.date.today() + datetime.timedelta(days=365),
    help="The expiration date of the option.",
)

T = (exercise_date - datetime.date.today()).days / 365  #

if page == "Black-Scholes-Merton":
    st.title("Black-Scholes-Merton Option Pricing Model")
    st.write(
        """
    The Black-Scholes-Merton model is a mathematical model for pricing European options. It assumes the underlying asset follows a geometric Brownian motion with constant drift and volatility.
    """
    )

    use_simulation = st.sidebar.checkbox(
        "Use Monte Carlo Simulation",
        help="Check to use Monte Carlo simulation instead of the analytical formula.",
    )

    if not use_simulation:
        st.header("Analytical Option Pricing")
        if st.button("Calculate Option Price"):
            try:
                BSM = BSMOptionPricing(
                    S=stock_price, K=strike_price, T=T, R=risk_free_rate, sigma=sigma
                )
                option_price = BSM.price(option_type=option_type.lower())
                st.success(f"Option Price: **{option_price:.4f}**")

                st.subheader("Sensitivity Analysis")
                vol_range = np.linspace(0.01, 1.0, 100)
                prices = []
                for vol in vol_range:
                    BSM_temp = BSMOptionPricing(
                        S=stock_price, K=strike_price, T=T, R=risk_free_rate, sigma=vol
                    )
                    price = BSM_temp.price(option_type=option_type.lower())
                    prices.append(price)

                fig, ax = plt.subplots()
                ax.plot(vol_range * 100, prices)
                ax.set_xlabel("Volatility (%)")
                ax.set_ylabel("Option Price")
                ax.set_title("Option Price vs. Volatility")
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error calculating option price: {e}")
    else:
        st.header("Monte Carlo Simulation Option Pricing")
        intervals = st.sidebar.slider(
            "Number of Time Steps:",
            min_value=50,
            max_value=500,
            step=50,
            value=252,
            help="Number of time steps in the simulation.",
        )

        simulations = st.sidebar.slider(
            "Number of Simulations:",
            min_value=1000,
            max_value=100000,
            step=1000,
            value=10000,
            help="Number of Monte Carlo simulation paths.",
        )

        num_paths = st.sidebar.slider(
            "Number of Paths to Plot:",
            min_value=1,
            max_value=100,
            step=1,
            value=5,
            help="Number of simulation paths to visualize.",
        )

        if st.button("Run Monte Carlo Simulation"):
            try:
                mc_model = MCOptionPricing(
                    S0=stock_price,
                    K=strike_price,
                    T=T,
                    R=risk_free_rate,
                    sigma=sigma,
                    intervals=intervals,
                    simulations=simulations,
                )
                option_price = mc_model.pricing(option_type=option_type.lower())
                st.success(f"Simulated Option Price: **{option_price:.4f}**")

                st.subheader("Simulated Asset Price Paths")
                fig, ax = mc_model.plot_simulated_paths(num_paths_to_plot=num_paths)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error in simulation: {e}")

elif page == "Merton Jump-Diffusion":
    st.title("Merton Jump-Diffusion Option Pricing Model")
    st.write(
        """
    The Merton Jump-Diffusion model extends the Black-Scholes-Merton model by incorporating random jumps in the underlying asset price, capturing sudden and significant changes in the market.
    """
    )

    use_simulation = st.sidebar.checkbox(
        "Use Monte Carlo Simulation",
        help="Check to use Monte Carlo simulation instead of the analytical formula.",
    )

    if not use_simulation:
        st.header("Analytical Option Pricing")
        if st.button("Calculate Option Price"):
            try:
                Merton = MertonJumpOptionPricing(
                    S=stock_price,
                    K=strike_price,
                    T=T,
                    R=risk_free_rate,
                    sigma=sigma,
                    lambda_=jump_intensity,
                    mu_jump=jump_mean,
                    sigma_jump=jump_volatility,
                )
                option_price = Merton.price(option_type=option_type.lower())
                st.success(f"Option Price: **{option_price:.4f}**")

                st.subheader("Sensitivity to Jump Intensity")
                intensity_range = np.linspace(0.0, 1.0, 50)
                prices = []
                for lam in intensity_range:
                    Merton_temp = MertonJumpOptionPricing(
                        S=stock_price,
                        K=strike_price,
                        T=T,
                        R=risk_free_rate,
                        sigma=sigma,
                        lambda_=lam,
                        mu_jump=jump_mean,
                        sigma_jump=jump_volatility,
                    )
                    price = Merton_temp.price(option_type=option_type.lower())
                    prices.append(price)

                fig, ax = plt.subplots()
                ax.plot(intensity_range, prices)
                ax.set_xlabel("Jump Intensity (λ)")
                ax.set_ylabel("Option Price")
                ax.set_title("Option Price vs. Jump Intensity")
                ax.grid(True)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error calculating option price: {e}")
    else:
        st.header("Monte Carlo Simulation Option Pricing")
        intervals = st.sidebar.slider(
            "Number of Time Steps:",
            min_value=50,
            max_value=500,
            step=50,
            value=252,
            help="Number of time steps in the simulation.",
        )

        simulations = st.sidebar.slider(
            "Number of Simulations:",
            min_value=1000,
            max_value=100000,
            step=1000,
            value=10000,
            help="Number of Monte Carlo simulation paths.",
        )

        num_paths = st.sidebar.slider(
            "Number of Paths to Plot:",
            min_value=1,
            max_value=100,
            step=1,
            value=5,
            help="Number of simulation paths to visualize.",
        )

        if st.button("Run Monte Carlo Simulation"):
            try:
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
                    sigma_jump=jump_volatility,
                )
                option_price = mc_jump_model.pricing(option_type=option_type.lower())
                st.success(f"Simulated Option Price: **{option_price:.4f}**")

                st.subheader("Simulated Asset Price Paths with Jumps")
                fig, ax = mc_jump_model.plot_simulated_paths(
                    num_paths_to_plot=num_paths
                )
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error in simulation: {e}")
