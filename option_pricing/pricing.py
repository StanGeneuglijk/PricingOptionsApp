import math
from scipy.stats import norm

import numpy as np 


########
#BSMf.
########
class BSMOptionPricing:

    def __init__(self,
                 S: float, K: float, T: float, R: float, sigma: float) -> None:
        self.S = S
        self.K = K
        self.T = T
        self.R = R
        self.sigma = sigma
        self.d1, self.d2 = self.calculate_d1_d2()

    def calculate_d1_d2(self) -> tuple:
        d1 = (math.log(self.S/self.K) + (self.R + 0.5*self.sigma**2) * self.T) / (self.sigma * math.sqrt(self.T))
        d2 = d1 - self.sigma * math.sqrt(self.T)
        return d1, d2
    
    def black_scholes(self, 
                      option_type: str = "call") -> float:
        try:
            if option_type.lower() == 'call':
                option_price = self.S * norm.cdf(self.d1) - math.exp(-self.R * self.T) * self.K * norm.cdf(self.d2)
            elif option_type.lower() == 'put':
                option_price = -self.S * norm.cdf(-self.d1) + math.exp(-self.R * self.T) * self.K * norm.cdf(-self.d2)
            else:
                raise ValueError("Invalid option type")
            return option_price
        except Exception as e:
            print(f"Error: {e}")
            
# #e.g. Usage
# S = 100        
# K = 110       
# T = 1         
# R = 0.05       
# sigma = 0.2   

# bsm_option = BSMOptionPricing(S, K, T, R, sigma)

# call_price = bsm_option.black_scholes(option_type="call")
# print(f"The theoretical price of the European call option is: {call_price}")


########
#BSMJumpf.
########

class MertonJumpOptionPricing:

    def __init__(self, 
                 S: float, K: float, T: float, R: float, sigma: float, 
                 lambda_: float, mu_jump: float, sigma_jump: float) -> None:
        self.S = S
        self.K = K
        self.T = T
        self.R = R
        self.sigma = sigma
        self.lambda_ = lambda_
        self.mu_jump = mu_jump
        self.sigma_jump = sigma_jump

    def calculate_d1_d2(self, sigma_adj: float) -> tuple:
        d1 = (math.log(self.S/self.K) + (self.R + 0.5*sigma_adj**2) * self.T) / (sigma_adj * math.sqrt(self.T))
        d2 = d1 - sigma_adj * math.sqrt(self.T)
        return d1, d2

    def merton_jump_diffusion(self, 
                              option_type: str = "call", max_terms: int = 50) -> float:
        price = 0.0
        for k in range(max_terms):
            r_k = self.R - self.lambda_ * (np.exp(self.mu_jump) - 1) + k * np.log(1 + self.mu_jump)
            sigma_k = math.sqrt(self.sigma**2 + k * (self.sigma_jump**2 / self.T))
            d1_k, d2_k = self.calculate_d1_d2(sigma_k)
            
            if option_type.lower() == 'call':
                price += (math.exp(-self.lambda_ * self.T) * (self.lambda_ * self.T)**k / math.factorial(k)) * \
                          (self.S * norm.cdf(d1_k) - self.K * math.exp(-r_k * self.T) * norm.cdf(d2_k))
            elif option_type.lower() == 'put':
                price += (math.exp(-self.lambda_ * self.T) * (self.lambda_ * self.T)**k / math.factorial(k)) * \
                          (-self.S * norm.cdf(-d1_k) + self.K * math.exp(-r_k * self.T) * norm.cdf(-d2_k))
            else:
                raise ValueError("Invalid option type")
        
        return price
    
# #e.g. Usage
# S0 = 100          
# K = 110        
# T = 1             
# R = 0.05          
# sigma = 0.2     
# intervals = 252   
# simulations = 10000
# lambda_ = 0.2
# mu_jump = 0.2
# sigma_jump = 0.2

# merton_option = MertonJumpOptionPricing(S, K, T, R, sigma, lambda_, mu_jump, sigma_jump)

# call_price = merton_option.merton_jump_diffusion(option_type="call")
# print(f"The theoretical price of the European call option with jumps (Merton model) is: {call_price}")

# #h.g.{