import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple
from scipy.stats import norm


@dataclass
class OptionPricingModel(ABC):
    """
    Abstract base class for option pricing models.

    Parameters:
    -----------
    S : float
        Current stock price.
    K : float
        Option strike price.
    T : float
        Time to maturity (in years).
    R : float
        Risk-free interest rate.
    sigma : float
        Volatility of the underlying asset.
    """

    S: float
    K: float
    T: float
    R: float
    sigma: float

    @abstractmethod
    def price(self, option_type: str = "call") -> float:
        """
        Abstract method to calculate the option price.
        """
        pass


@dataclass
class BSMOptionPricing(OptionPricingModel):
    """
    Black-Scholes-Merton Option Pricing model.
    """

    def _calculate_d1_d2(self) -> Tuple[float, float]:
        """
        Calculate d1 and d2 used in the Black-Scholes formula.

        Returns:
        --------
        Tuple[float, float]
            The values of d1 and d2.
        """
        d1 = (math.log(self.S / self.K) + (self.R + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * math.sqrt(self.T)
        )
        d2 = d1 - self.sigma * math.sqrt(self.T)
        return d1, d2

    def price(self, option_type: str = "call") -> float:
        """
        Calculate the option price using the Black-Scholes-Merton model.

        Parameters:
        -----------
        option_type : str, optional
            The type of option ('call' or 'put'). Default is 'call'.

        Returns:
        --------
        float
            The calculated option price.
        """
        d1, d2 = self._calculate_d1_d2()
        if option_type.lower() == "call":
            option_price = self.S * norm.cdf(d1) - self.K * math.exp(
                -self.R * self.T
            ) * norm.cdf(d2)
        elif option_type.lower() == "put":
            option_price = self.K * math.exp(-self.R * self.T) * norm.cdf(
                -d2
            ) - self.S * norm.cdf(-d1)
        else:
            raise ValueError("Invalid option type. Must be 'call' or 'put'.")
        return option_price


@dataclass
class MertonJumpOptionPricing(OptionPricingModel):
    """
    Merton Jump-Diffusion Option Pricing model.

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

    def _calculate_kappa(self) -> float:
        """
        Calculate kappa, the expected relative jump size.

        Returns:
        --------
        float
            The expected relative jump size.
        """
        return math.exp(self.mu_jump + 0.5 * self.sigma_jump**2) - 1

    def _calculate_adjusted_parameters(self, n: int) -> Tuple[float, float, float]:
        """
        Calculate adjusted risk-free rate and volatility for the n-th term.

        Parameters:
        -----------
        n : int
            The number of jumps.

        Returns:
        --------
        Tuple[float, float, float]
            Adjusted risk-free rate, volatility, and drift.
        """
        kappa = self._calculate_kappa()
        lambda_kappa = self.lambda_ * kappa
        r_adj = self.R - lambda_kappa + n * self.mu_jump / self.T
        sigma_n = math.sqrt(self.sigma**2 + n * self.sigma_jump**2 / self.T)
        return r_adj, sigma_n

    def price(self, option_type: str = "call", max_terms: int = 50) -> float:
        """
        Calculate the option price using the Merton Jump-Diffusion model.

        Parameters:
        -----------
        option_type : str, optional
            The type of option ('call' or 'put'). Default is 'call'.
        max_terms : int, optional
            Maximum number of terms to use in the summation for the jump terms. Default is 50.

        Returns:
        --------
        float
            The calculated option price.
        """
        price = 0.0
        kappa = self._calculate_kappa()
        lambda_T = self.lambda_ * self.T
        for n in range(max_terms):
            poisson_prob = (math.exp(-lambda_T) * (lambda_T) ** n) / math.factorial(n)
            r_adj, sigma_n = self._calculate_adjusted_parameters(n)
            d1 = (math.log(self.S / self.K) + (r_adj + 0.5 * sigma_n**2) * self.T) / (
                sigma_n * math.sqrt(self.T)
            )
            d2 = d1 - sigma_n * math.sqrt(self.T)
            if option_type.lower() == "call":
                term_price = self.S * math.exp(
                    -self.lambda_ * kappa * self.T
                ) * norm.cdf(d1) - self.K * math.exp(-self.R * self.T) * norm.cdf(d2)
            elif option_type.lower() == "put":
                term_price = self.K * math.exp(-self.R * self.T) * norm.cdf(
                    -d2
                ) - self.S * math.exp(-self.lambda_ * kappa * self.T) * norm.cdf(-d1)
            else:
                raise ValueError("Invalid option type. Must be 'call' or 'put'.")
            price += poisson_prob * term_price
        return price
