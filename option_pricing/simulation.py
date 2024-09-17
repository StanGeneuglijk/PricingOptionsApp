import math
import numpy as np
import matplotlib.pyplot as plt

class MCOptionPricing:
    """
    Monte Carlo Option Pricing model for options without jumps.
    
    Parameters:
    -----------
    S0 : float
        Initial stock price.
    K : float
        Option strike price.
    T : float
        Time to maturity (in years).
    R : float
        Risk-free interest rate.
    sigma : float
        Volatility of the underlying asset.
    intervals : int
        Number of time intervals for the simulation.
    simulations : int
        Number of Monte Carlo simulations to run.
    seed : int, optional
        Random seed for reproducibility.
    """

    def __init__(self, 
                 S0: float, K: float, T: float, R: float, sigma: float, 
                 intervals: int, simulations: int, seed: int = None) -> None:
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

    def _simulate_paths(self) -> None:
        """
        Simulate the asset price paths using Monte Carlo simulation.
        """
        drift = (self.R - 0.5 * self.sigma**2) * self.dt
        diffusion = self.sigma * math.sqrt(self.dt)

        for i in range(1, self.intervals):
            self.price_array[:, i] = self.price_array[:, i - 1] * np.exp(drift + diffusion * self.Z[:, i - 1])

        self.terminal_price = self.price_array[:, -1]
        self.avg_terminal_price = np.mean(self.terminal_price)

    def pricing(self, option_type: str = "call") -> float:
        """
        Price the option using Monte Carlo simulation.

        Parameters:
        -----------
        option_type : str, optional
            The type of option ('call' or 'put'). Default is 'call'.

        Returns:
        --------
        float
            The Monte Carlo estimated option price.
        """
        self._simulate_paths()

        try:
            if option_type.lower() == "call":
                terminal_profit = np.maximum(self.terminal_price - self.K, 0)
            elif option_type.lower() == "put":
                terminal_profit = np.maximum(self.K - self.terminal_price, 0)
            else:
                raise ValueError("Invalid option type. Must be 'call' or 'put'.")
            
            avg_terminal_profit = np.mean(terminal_profit)
            discounted_profit = np.exp(-self.R * self.T) * avg_terminal_profit

            return discounted_profit
        except Exception as e:
            raise RuntimeError(f"Error in option pricing: {e}")

    def plot_simulated_paths(self, num_paths_to_plot: int = 10):
        """
        Plot a selection of the simulated asset price paths.

        Parameters:
        -----------
        num_paths_to_plot : int, optional
            Number of paths to plot. Default is 10.

        Returns:
        --------
        fig, ax : Matplotlib figure and axes
            The figure and axes objects with the simulated paths plotted.
        """
        if num_paths_to_plot > self.simulations:
            num_paths_to_plot = self.simulations

        fig, ax = plt.subplots(figsize=(10, 6))

        for i in range(num_paths_to_plot):
            ax.plot(np.linspace(0, self.T, self.intervals), self.price_array[i, :], lw=1)

        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Asset Price')
        ax.set_title(f'Simulated Asset Paths ({num_paths_to_plot} paths)')
        ax.grid(True)

        return fig, ax


class MCJumpOptionPricing:
    """
    Monte Carlo Option Pricing model for options with jumps (Merton Jump Diffusion).
    
    Parameters:
    -----------
    S0 : float
        Initial stock price.
    K : float
        Option strike price.
    T : float
        Time to maturity (in years).
    R : float
        Risk-free interest rate.
    sigma : float
        Volatility of the underlying asset.
    intervals : int
        Number of time intervals for the simulation.
    simulations : int
        Number of Monte Carlo simulations to run.
    lambda_ : float
        Jump intensity (average number of jumps per year).
    mu_jump : float
        Mean jump size.
    sigma_jump : float
        Volatility of the jump size.
    seed : int, optional
        Random seed for reproducibility.
    """

    def __init__(self, 
                 S0: float, K: float, T: float, R: float, sigma: float, 
                 intervals: int, simulations: int, lambda_: float, 
                 mu_jump: float, sigma_jump: float, seed: int = None) -> None:
        self.S0 = S0
        self.K = K
        self.T = T
        self.R = R
        self.sigma = sigma
        self.intervals = intervals
        self.dt = self.T / self.intervals
        self.simulations = simulations
        self.lambda_ = lambda_
        self.mu_jump = mu_jump
        self.sigma_jump = sigma_jump
        self.seed = seed

        if self.seed is not None:
            np.random.seed(self.seed)

        self.Z = np.random.standard_normal((self.simulations, self.intervals))
        self.J = np.random.standard_normal((self.simulations, self.intervals))
        self.N = np.random.poisson(self.lambda_ * self.dt, (self.simulations, self.intervals))
        self.price_array = np.zeros((self.simulations, self.intervals))
        self.price_array[:, 0] = self.S0
        self.terminal_price = None
        self.avg_terminal_price = None

    def _simulate_paths(self) -> None:
        """
        Simulate the asset price paths including jump components.
        """
        drift = (self.R - 0.5 * self.sigma**2 - self.lambda_ * 
                 (np.exp(self.mu_jump + 0.5 * self.sigma_jump**2) - 1)) * self.dt
        diffusion = self.sigma * math.sqrt(self.dt)

        for i in range(1, self.intervals):
            jump_component = (np.exp(self.mu_jump + self.sigma_jump * self.J[:, i - 1]) - 1) * self.N[:, i - 1]
            self.price_array[:, i] = self.price_array[:, i - 1] * np.exp(drift + diffusion * self.Z[:, i - 1]) * (1 + jump_component)

        self.terminal_price = self.price_array[:, -1]
        self.avg_terminal_price = np.mean(self.terminal_price)

    def pricing(self, option_type: str = "call") -> float:
        """
        Price the option using Monte Carlo simulation with jumps.

        Parameters:
        -----------
        option_type : str, optional
            The type of option ('call' or 'put'). Default is 'call'.

        Returns:
        --------
        float
            The Monte Carlo estimated option price with jumps.
        """
        self._simulate_paths()

        try:
            if option_type.lower() == "call":
                terminal_profit = np.maximum(self.terminal_price - self.K, 0)
            elif option_type.lower() == "put":
                terminal_profit = np.maximum(self.K - self.terminal_price, 0)
            else:
                raise ValueError("Invalid option type. Must be 'call' or 'put'.")
            
            avg_terminal_profit = np.mean(terminal_profit)
            discounted_profit = np.exp(-self.R * self.T) * avg_terminal_profit

            return discounted_profit
        except Exception as e:
            raise RuntimeError(f"Error in option pricing with jumps: {e}")

    def plot_simulated_paths(self, num_paths_to_plot: int = 10):
        """
        Plot a selection of the simulated asset price paths with jumps.

        Parameters:
        -----------
        num_paths_to_plot : int, optional
            Number of paths to plot. Default is 10.

        Returns:
        --------
        fig, ax : Matplotlib figure and axes
            The figure and axes objects with the simulated paths plotted.
        """
        if num_paths_to_plot > self.simulations:
            num_paths_to_plot = self.simulations

        fig, ax = plt.subplots(figsize=(10, 6))

        for i in range(num_paths_to_plot):
            ax.plot(np.linspace(0, self.T, self.intervals), self.price_array[i, :], lw=1)

        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Asset Price')
        ax.set_title(f'Simulated Asset Paths with Jumps ({num_paths_to_plot} paths)')
        ax.grid(True)

        return fig, ax
