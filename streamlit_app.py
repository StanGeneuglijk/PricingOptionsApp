import streamlit as st
import datetime
import matplotlib.pyplot as plt
from option_pricing.pricing import BSMOptionPricing, MertonJumpOptionPricing
from option_pricing.simulation import MCOptionPricing, MCJumpOptionPricing

# Method input
st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Choose: ", 
    ["Black-Scholes-Merton", 
     "Merton Jump-Diffusion"]
)

# Parameters input
st.sidebar.subheader("Parameters:")

option_type = st.sidebar.selectbox(
    "Option Type: ",
    ["Call", "Put"]
)

stock_price = st.sidebar.number_input(
    'Stock Price', 
    min_value=0.0, 
    step=5.0
)

strike_price = st.sidebar.number_input(
    'Strike Price', 
    min_value=0.0, 
    step=5.0
)

risk_free_rate = st.sidebar.slider(
    'Risk-Free Rate (%)', 
    min_value=0.0, 
    max_value=10.0, 
    step=0.5
) / 100

sigma = st.sidebar.slider(
    'Volatility (%)', 
    min_value=0.0, 
    max_value=100.0, 
    step=5.0
) / 100

exercise_date = st.sidebar.date_input(
    'Exercise Date', 
    min_value=datetime.datetime.today(), 
    value=datetime.datetime.today() + datetime.timedelta(days=365)
)

T = (exercise_date - datetime.datetime.now().date()).days / 365

# Black-Scholes-Merton Page
if page == "Black-Scholes-Merton":
    st.title("Black-Scholes-Merton Option Pricing")

    use_simulation = st.sidebar.checkbox("Monte Carlo Simulation")

    if not use_simulation:
        if st.button('Calculate Theoretical Option Price'):
            BSM = BSMOptionPricing(
                S=stock_price,
                K=strike_price,
                T=T,
                R=risk_free_rate,
                sigma=sigma
            )
            option_price = BSM.black_scholes(
                option_type=option_type
            )
            st.write(f'Option Price: {round(option_price, 4)}')
    else:
        intervals = st.slider(
            'Number of sub-intervals', 
            min_value=50, 
            max_value=500, 
            step=50
            )
        
        simulations = st.slider(
            'Number of Simulations', 
            min_value=1000, 
            max_value=10000, 
            step=1000
            )
        
        num_paths = st.slider(
            '(Visualization) Number of Simulation Paths', 
            min_value=1, 
            max_value=100, 
            step=1
            )
        
        if st.button('Calculate Simulation Option Price'):
            mc_model = MCOptionPricing(
                S0=stock_price,
                K=strike_price,
                T=T,
                R=risk_free_rate,
                sigma=sigma,
                intervals=intervals,
                simulations=simulations
            )
            option_price = mc_model.pricing(
                option_type=option_type.lower()
            )
            st.write(f'Option Price: {round(option_price, 4)}')
            
            st.write("Simulation Path:")
            st.pyplot(
                mc_model.plot_simulated_paths(
                    num_paths_to_plot=num_paths
                )
            )

# Merton Jump-Diffusion Page
elif page == "Merton Jump-Diffusion":
    st.title("Merton Jump-Diffusion Option Pricing")

    use_simulation = st.sidebar.checkbox("Monte Carlo Simulation")

    jump_intensity = st.sidebar.slider(
        'Jump Intensity', 
        min_value=0.0, 
        max_value=1.0, 
        step=0.1
    )
    
    jump_mean = st.sidebar.slider(
        'Jump Mean', 
        min_value=0.0, 
        max_value=2.0,
        step=0.1
    )
    
    jump_volatility = st.sidebar.slider(
        'Jump Volatility (%)', 
        min_value=0.0, 
        max_value=100.0, 
        step=5.0
    ) / 100

    if not use_simulation:
        if st.button('Calculate Theoretical Option Price'):
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
            option_price = Merton.merton_jump_diffusion(
                option_type=option_type
            )
            st.write(f'Option Price: {round(option_price, 4)}')
    else:
        intervals = st.slider(
            'Number of sub-intervals', 
            min_value=50, 
            max_value=500, 
            step=50
            )
        
        simulations = st.slider(
            'Number of Simulations', 
            min_value=1000, 
            max_value=10000, 
            step=1000
            )
        
        num_paths = st.slider(
            '(Visualization) Number of Simulation Paths', 
            min_value=1, 
            max_value=100, 
            step=1
            )
        
        if st.button('Calculate Simulation Option Price'):
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
            option_price = mc_jump_model.pricing(
                option_type=option_type.lower()
            )
            st.write(f'Simulated Option Price (Merton Jump-Diffusion): {round(option_price, 4)}')
            
            st.write("Simulation Path:")
            st.pyplot(
                mc_jump_model.plot_simulated_paths(
                    num_paths_to_plot=num_paths
                )
            )
