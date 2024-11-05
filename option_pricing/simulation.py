import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class MonteCarloOptionPricing(ABC):
    """
    Abstract base class for Monte Carlo Option Pricing models.

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

    S0: float
    K: float
    T: float
    R: float
    sigma: float
    intervals: int
    simulations: int
    seed: Optional[int] = None
    dt: float = field(init=False)
    price_array: np.ndarray = field(init=False)
    terminal_price: np.ndarray = field(init=False)
    avg_terminal_price: float = field(init=False)

    def __post_init__(self):
        self.dt = self.T / self.intervals
        if self.seed is not None:
            np.random.seed(self.seed)
        self.price_array = np.zeros((self.simulations, self.intervals))
        self.price_array[:, 0] = self.S0
        self.terminal_price = np.zeros(self.simulations)
        self.avg_terminal_price = 0.0

    @abstractmethod
    def _simulate_paths(self) -> None:
        """
        Abstract method to simulate the asset price paths.
        """
        pass

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
        if option_type.lower() == "call":
            terminal_profit = np.maximum(self.terminal_price - self.K, 0)
        elif option_type.lower() == "put":
            terminal_profit = np.maximum(self.K - self.terminal_price, 0)
        else:
            raise ValueError("Invalid option type. Must be 'call' or 'put'.")
        avg_terminal_profit = np.mean(terminal_profit)
        discounted_profit = np.exp(-self.R * self.T) * avg_terminal_profit
        return discounted_profit

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
        time_grid = np.linspace(0, self.T, self.intervals)
        for i in range(num_paths_to_plot):
            ax.plot(time_grid, self.price_array[i, :], lw=1)

        ax.set_xlabel("Time (years)")
        ax.set_ylabel("Asset Price")
        ax.set_title(f"Simulated Asset Paths ({num_paths_to_plot} paths)")
        ax.grid(True)

        plt.show()
        return fig, ax


@dataclass
class MCOptionPricing(MonteCarloOptionPricing):
    """
    Monte Carlo Option Pricing model for options without jumps.
    """

    def _simulate_paths(self) -> None:
        """
        Simulate the asset price paths using Monte Carlo simulation.
        """
        Z = np.random.standard_normal((self.simulations, self.intervals - 1))
        drift = (self.R - 0.5 * self.sigma**2) * self.dt
        diffusion = self.sigma * math.sqrt(self.dt)
        for i in range(1, self.intervals):
            self.price_array[:, i] = self.price_array[:, i - 1] * np.exp(
                drift + diffusion * Z[:, i - 1]
            )
        self.terminal_price = self.price_array[:, -1]
        self.avg_terminal_price = np.mean(self.terminal_price)


@dataclass
class MCJumpOptionPricing(MonteCarloOptionPricing):
    """
    Monte Carlo Option Pricing model for options with jumps (Merton Jump Diffusion).

    Parameters:
    -----------
    lambda_ : float
        Jump intensity (average number of jumps per year).
    mu_jump : float
        Mean of the logarithm of the jump size.
    sigma_jump : float
        Standard deviation of the logarithm of the jump size.
    """

    lambda_: float
    mu_jump: float
    sigma_jump: float

    def _simulate_paths(self) -> None:
        """
        Simulate the asset price paths including jump components.
        """
        Z = np.random.standard_normal((self.simulations, self.intervals - 1))
        drift = (
            self.R
            - 0.5 * self.sigma**2
            - self.lambda_ * (math.exp(self.mu_jump + 0.5 * self.sigma_jump**2) - 1)
        ) * self.dt
        diffusion = self.sigma * math.sqrt(self.dt)
        for i in range(1, self.intervals):
            N_jumps = np.random.poisson(self.lambda_ * self.dt, self.simulations)
            if N_jumps.any():
                jump_sizes = np.random.normal(
                    self.mu_jump, self.sigma_jump, self.simulations
                )
                jump_component = np.exp(jump_sizes * N_jumps)
            else:
                jump_component = np.ones(self.simulations)
            self.price_array[:, i] = (
                self.price_array[:, i - 1]
                * np.exp(drift + diffusion * Z[:, i - 1])
                * jump_component
            )
        self.terminal_price = self.price_array[:, -1]
        self.avg_terminal_price = np.mean(self.terminal_price)
