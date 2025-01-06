from pydantic import BaseModel, Field
from typing import List, Optional, Dict

profile_template = """{
  "name": null,
  "age": null,
  "gender": null,
  "location": null,
  "education_level": null,
  "occupation": null,
  "experience_level": null,
  "primary_goal": null,
  "time_horizon": null,
  "risk_tolerance": null,
  "investment_style": null,
  "trading_frequency": null,
  "preferred_assets": [],
  "trading_instruments": [],
  "analysis_method": [],
  "portfolio_size": null,
  "asset_allocation": {},
  "diversification_level": null,
  "risk_mitigation_tools": [],
  "portfolio_rebalancing_strategy": null,
  "drawdown_tolerance": null,
  "emotional_response_to_market": null,
  "decision_making_process": null,
  "reaction_to_losses": null,
  "impact_of_media_news": null,
  "trading_platforms_used": [],
  "use_of_tools_technologies": [],
  "technical_skills": null,
  "average_annual_return": null,
  "best_investment_trade": null,
  "worst_investment_trade": null,
  "consistency_of_performance": null,
  "influences_on_decision": [],
  "ethical_investment_considerations": [],
  "learning_sources": []
}"""

class InvestorTraderProfile(BaseModel):
    # Basic Information
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    education_level: Optional[str] = None
    occupation: Optional[str] = None
    experience_level: Optional[str] = None  # Novice, Intermediate, Advanced
    
    # Investment/Trading Objectives
    primary_goal: Optional[str] = None  # Capital appreciation, Income generation, etc.
    time_horizon: Optional[str] = None  # Short-term, Medium-term, Long-term
    risk_tolerance: Optional[str] = None  # Low, Medium, High
    
    # Investment/Trading Strategy
    investment_style: Optional[str] = None  # Investor, Trader, Speculator
    trading_frequency: Optional[str] = None  # Rare, Moderate, Frequent
    preferred_assets: Optional[List[str]] = []  # Stocks, ETFs, Options, etc.
    trading_instruments: Optional[List[str]] = []  # Stocks, Options, Futures, etc.
    analysis_method: Optional[List[str]] = []  # Technical, Fundamental, Quantitative, Sentiment
    
    # Portfolio Composition
    portfolio_size: Optional[float] = None  # E.g., $10,000, $100,000, etc.
    asset_allocation: Optional[Dict[str, float]] = {}  # Example: {'Equities': 50, 'Bonds': 30, 'Cash': 20}
    diversification_level: Optional[str] = None  # Highly diversified, Moderately diversified, Concentrated
    
    # Risk Management Practices
    risk_mitigation_tools: Optional[List[str]] = []  # Stop loss, Hedging, Diversification
    portfolio_rebalancing_strategy: Optional[str] = None  # Regular, Ad-hoc
    drawdown_tolerance: Optional[float] = None  # e.g., 10% loss tolerance
    
    # Behavioral Characteristics
    emotional_response_to_market: Optional[str] = None  # Calm under pressure, Nervous, etc.
    decision_making_process: Optional[str] = None  # Data-driven, Impulsive, Collaborative
    reaction_to_losses: Optional[str] = None  # Cut losses, Hold through downturns, etc.
    impact_of_media_news: Optional[str] = None  # Highly influenced, Minimal impact
    
    # Technological Proficiency
    trading_platforms_used: Optional[List[str]] = []  # TD Ameritrade, MetaTrader, Robo-advisor platforms
    use_of_tools_technologies: Optional[List[str]] = []  # Algorithmic trading, Mobile apps, etc.
    technical_skills: Optional[str] = None  # High, Moderate, Low
    
    # Performance and Record
    average_annual_return: Optional[float] = None  # Example: 5%
    best_investment_trade: Optional[str] = None  # Description of best trade
    worst_investment_trade: Optional[str] = None  # Description of worst trade
    consistency_of_performance: Optional[str] = None  # Consistent, Mixed, Mostly losses
    
    # Additional Characteristics
    influences_on_decision: Optional[List[str]] = []  # Financial news, Influential investors, etc.
    ethical_investment_considerations: Optional[List[str]] = []  # ESG, SRI, Impact investing
    learning_sources: Optional[List[str]] = []  # Books, Podcasts, Courses, Mentorship, etc.

    class Config:
        str_min_length = 1
        str_strip_whitespace = True

    # Function to convert profile to dict
    def to_dict(self):
        # Use Pydantic's built-in .dict() method and filter out None values if desired
        return self.model_dump()

if __name__ == "__main__":
    # Example of how to create an instance
    example_profile = InvestorTraderProfile(
    )



    out = example_profile.model_dump_json(indent=2)
    print(out)