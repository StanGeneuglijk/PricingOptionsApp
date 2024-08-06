import math
from scipy.stats import norm

import matplotlib.pyplot as plt

import numpy as np 


#1.1) PricingScript
#yes
class BSMOptionPricing:

    def __init__(self,
                 S: float, K: float, T: float, R: float, sigma: float) -> None:
        self.S = S
        self.K = K
        self.T = T
        self.R = R
        self.sigma = sigma
        self.d1, self.d2 = self.calculate_d1_d2()

    def calculate_d1_d2(self) -> float:
        d1 = (math.log(self.S/self.K) + (self.R +.5*self.sigma**2)*self.T)/(self.sigma*math.sqrt(self.T))
        d2 = (math.log(self.S/self.K) - (self.R +.5*self.sigma**2)*self.T)/(self.sigma*math.sqrt(self.T))
        return d1, d2
    
    #BSMf.
    def black_scholes(self, 
                      option_type: str = "call") -> float:
        d1, d2 = self.calculate_d1_d2()
        try:
            if option_type.lower() == 'call':
                option_price = self.S * norm.cdf(self.d1, 0, 1) - math.exp(-self.R*self.T)*self.K*norm.cdf(self.d2, 0, 1)
            elif option_type.lower() == 'put':
                option_price = -self.S * norm.cdf(-self.d1, 0, 1) + math.exp(-self.R*self.T)*self.K*norm.cdf(-self.d2, 0, 1)
            else:
                raise ValueError("Invalid option type")
            return option_price
        except Exception:
            print(f"Error: {Exception}")

    #+BSMf. Greeks e.g. Delta
    def delta(self, 
              option_type: str = "call") -> float:
        try:
            if option_type.lower() == 'call':
                option_delta = norm.cdf(self.d1, 0, 1)
            elif option_type.lower() == 'put':
                option_delta = - norm.cdf(-self.d1, 0, 1)
            else:
                raise ValueError("Invalid option type")
            return option_delta
        except Exception:
            print(f"Error: {Exception}")

    def plot_delta(self, 
                   range_S: list, range_T: list, option_type: str = "call") -> None:
        original_S = self.S  
        original_T = self.T 
        try:
            plt.figure(figsize=(8, 6))
            sns.set(style="whitegrid")
            for T in range_T:
                self.T = T
                deltas = []
                for S in range_S:
                    self.S = S
                    self.d1, self.d2 = self.calculate_d1_d2()
                    deltas.append(self.delta(option_type))
                plt.plot(range_S, deltas, label=f'T={T} years', linewidth=2)
            self.S = original_S
            self.T = original_T
            self.d1, self.d2 = self.calculate_d1_d2()
            plt.xlabel('Asset Price S', fontsize=14)
            plt.ylabel('Delta', fontsize=14)
            plt.title(f'Delta for {option_type.capitalize()} Option', fontsize=16)
            plt.legend(title='Maturity', fontsize=12)
            plt.grid(False)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            sns.despine()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Error: {e}")


    #+ BSMf. Implied Volatility
    def vega(self, option_type: str='call') -> float:
        try:
            if option_type.lower()=='call' or option_type.lower()=='put':
                option_vega = self.S * norm.pdf(self.d1) * math.sqrt(self.T)
            else:
                raise ValueError("Invalid option type")
            return option_vega
        except Exception:
            print(print(f"Error: {Exception}"))

    def implied_vol(self, observed_option_price: float, option_type: str='call', max_iter: int = 250, tol: float = 1e-4) -> float:
        sigma_old = self.sigma
        converged = False
        for _ in range(max_iter):
            self.d1, self.d2 = self.calculate_d1_d2()
            option_price = self.black_scholes(option_type)
            option_price_diff = option_price - observed_option_price
            option_vega = self.vega()
            sigma_new = self.sigma - option_price_diff / (option_vega + 1e-10)
            if abs(sigma_new - self.sigma) <= tol:
                converged = True
                implied_vol = sigma_new
                break
            self.sigma = sigma_new
        else:
            implied_vol = sigma_new  
        self.sigma = sigma_old
        self.d1, self.d2 = self.calculate_d1_d2()
        if not converged:
            print(f"Implied volatility non-convergent g. {max_iter} iterations.")
        return implied_vol

    def plot_implied_vol(self, observed_option_price: float, range_K: list, range_T: list, option_type: str = "call") -> None:
        original_K = self.K
        original_T = self.T
        try:
            plt.figure(figsize=(8, 6))
            sns.set(style="whitegrid")
            for T in range_T:
                volatilities = []
                for K in range_K:
                    self.K = K
                    self.T = T
                    implied_volatility = self.implied_vol(observed_option_price, option_type)
                    volatilities.append(implied_volatility)
                plt.plot(range_K, volatilities, label=f'T={T} years', linewidth=2)
            self.K = original_K
            self.T = original_T
            self.d1, self.d2 = self.calculate_d1_d2()
            plt.xlabel('Strike Price K', fontsize=14)
            plt.ylabel('Implied Volatility', fontsize=14)
            plt.title(f'Implied Volatility for {option_type.capitalize()} Option', fontsize=16)
            plt.legend(title='Maturity', fontsize=12)
            plt.grid(False)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            sns.despine()
            plt.tight_layout()
            plt.show()
        except Exception:
            print(f"Error: {Exception}")


