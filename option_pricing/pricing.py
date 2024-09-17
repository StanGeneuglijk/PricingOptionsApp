import math
import numpy as np
from scipy.stats import norm


class BSMOptionPricing:
    """
    Black-Scholes-Merton Option Pricing model.
    
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

    def __init__(self, S: float, K: float, T: float, R: float, sigma: float) -> None:
        self.S = S
        self.K = K
        self.T = T
        self.R = R
        self.sigma = sigma
        self.d1, self.d2 = self._calculate_d1_d2()

    def _calculate_d1_d2(self) -> tuple[float, float]:
        """
        Internal method to calculate d1 and d2 used in the Black-Scholes formula.
        
        Returns:
        --------
        tuple[float, float]
            The values of d1 and d2.
        """
        try:
            d1 = (math.log(self.S / self.K) + (self.R + 0.5 * self.sigma**2) * self.T) / (self.sigma * math.sqrt(self.T))
            d2 = d1 - self.sigma * math.sqrt(self.T)
            return d1, d2
        except ValueError as e:
            raise ValueError(f"Error in calculating d1 and d2: {e}")

    def black_scholes(self, option_type: str = "call") -> float:
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
        try:
            if option_type.lower() == 'call':
                option_price = (self.S * norm.cdf(self.d1) - 
                                math.exp(-self.R * self.T) * self.K * norm.cdf(self.d2))
            elif option_type.lower() == 'put':
                option_price = (-self.S * norm.cdf(-self.d1) + 
                                 math.exp(-self.R * self.T) * self.K * norm.cdf(-self.d2))
            else:
                raise ValueError("Invalid option type. Must be 'call' or 'put'.")
            return option_price
        except Exception as e:
            raise RuntimeError(f"Error in Black-Scholes pricing: {e}")


class MertonJumpOptionPricing:
    """
    Merton Jump-Diffusion Option Pricing model.

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
    lambda_ : float
        Jump intensity (average number of jumps per year).
    mu_jump : float
        Mean of the jump size.
    sigma_jump : float
        Volatility of the jump size.
    """

    def __init__(self, S: float, K: float, T: float, R: float, sigma: float, 
                 lambda_: float, mu_jump: float, sigma_jump: float) -> None:
        self.S = S
        self.K = K
        self.T = T
        self.R = R
        self.sigma = sigma
        self.lambda_ = lambda_
        self.mu_jump = mu_jump
        self.sigma_jump = sigma_jump

    def _calculate_d1_d2(self, sigma_adj: float) -> tuple[float, float]:
        """
        Internal method to calculate d1 and d2 adjusted for jump risk.
        
        Parameters:
        -----------
        sigma_adj : float
            Adjusted volatility that accounts for jump risk.
        
        Returns:
        --------
        tuple[float, float]
            Adjusted values of d1 and d2.
        """
        try:
            d1 = (math.log(self.S / self.K) + (self.R + 0.5 * sigma_adj**2) * self.T) / (sigma_adj * math.sqrt(self.T))
            d2 = d1 - sigma_adj * math.sqrt(self.T)
            return d1, d2
        except ValueError as e:
            raise ValueError(f"Error in calculating adjusted d1 and d2: {e}")

    def merton_jump_diffusion(self, option_type: str = "call", max_terms: int = 50) -> float:
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
        try:
            price = 0.0
            for k in range(max_terms):
                r_k = self.R - self.lambda_ * (np.exp(self.mu_jump) - 1) + k * np.log(1 + self.mu_jump)
                sigma_k = math.sqrt(self.sigma**2 + k * (self.sigma_jump**2 / self.T))
                d1_k, d2_k = self._calculate_d1_d2(sigma_k)
                
                jump_weight = math.exp(-self.lambda_ * self.T) * (self.lambda_ * self.T)**k / math.factorial(k)
                
                if option_type.lower() == 'call':
                    price += jump_weight * (self.S * norm.cdf(d1_k) - self.K * math.exp(-r_k * self.T) * norm.cdf(d2_k))
                elif option_type.lower() == 'put':
                    price += jump_weight * (-self.S * norm.cdf(-d1_k) + self.K * math.exp(-r_k * self.T) * norm.cdf(-d2_k))
                else:
                    raise ValueError("Invalid option type. Must be 'call' or 'put'.")
            
            return price
        except Exception as e:
            raise RuntimeError(f"Error in Merton Jump-Diffusion pricing: {e}")
