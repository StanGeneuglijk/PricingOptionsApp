#h.g.{
import math
from scipy.stats import norm 

import matplotlib.pyplot as plt

import numpy as np 

class MCOptionPricing:
    
    def __init__(self, 
                 S0: float, K: float, T: float, R: float, sigma: float, intervals: int, simulations: int, seed: int = None) -> None:
        self.S0 = S0
        self.K = K
        self.T = T
        self.R = R
        self.sigma = sigma
        self.intervals = intervals
        self.dt = self.T / self.intervals
        self.simulations = simulations
        self.seed = seed

        if self.seed is not None:
            np.random.seed(self.seed)

        self.Z = np.random.standard_normal((self.simulations, self.intervals))
        self.price_array = np.zeros((self.simulations, self.intervals))
        self.price_array[:, 0] = self.S0
        self.terminal_price = None
        self.avg_terminal_price = None

    #Euler Scheme
    def simulation(self) -> float:

        drift = (self.R - 0.5 * self.sigma**2) * self.dt

        diffusion = self.sigma * np.sqrt(self.dt)

        for i in range(1, self.intervals):
            self.price_array[:, i] = self.price_array[:, i - 1] * np.exp(drift + diffusion * self.Z[:, i - 1])

        self.terminal_price = self.price_array[:, -1]

        self.avg_terminal_price = np.mean(self.terminal_price)
        
        return self.avg_terminal_price

    #+MCf.
    def pricing(self, option_type: str = "call") -> float:

        self.simulation()

        try: 

            if option_type.lower() == "call":
                terminal_profit = np.maximum(self.terminal_price - self.K, 0)

            elif option_type.lower() == "put":
                terminal_profit = np.maximum(-self.terminal_price + self.K, 0)

            else:
                raise ValueError("Invalid option type")
            
            avg_terminal_profit = np.mean(terminal_profit)

            discounted_profit = np.exp(-self.R * self.T) * avg_terminal_profit

            return discounted_profit
        
        except Exception:
            
            print(print(f"Error: {Exception}"))

    def plot_simulated_paths(self, num_paths_to_plot: int = 10) -> None:
        if num_paths_to_plot > self.simulations:
            num_paths_to_plot = self.simulations
        plt.figure(figsize=(10, 6))
        for i in range(num_paths_to_plot):
            plt.plot(np.linspace(0, self.T, self.intervals), self.price_array[i, :], lw=1)

        plt.xlabel('Time (years)')
        plt.ylabel('Asset Price')
        plt.title(f'Simulated Asset Paths ({num_paths_to_plot} paths)')
        plt.grid(False)
        plt.show()
