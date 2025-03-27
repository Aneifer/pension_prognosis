import numpy as np
import pandas as pd
import os

# Set the random seed for reproducibility
np.random.seed(42)

# Simulation parameters
start_sim_year = 1954
end_sim_year = 2024
max_individuals = 10000

# Pension calculation parameters
base_pension_value = 5.0         # Base pension value in 1954 in €
pension_growth_rate = 0.03       # Annual growth rate of the pension value

# Dynamic reference salary parameters
initial_reference_salary = 20000  # Average salary in 1954 in €
reference_growth_rate = 0.011     # Annual growth rate of the reference salary (1.1%)

# Pension contribution parameters
pension_contribution_rate = 0.186  # Total contribution rate (18.6% of gross salary)

# Dictionaries to aggregate annual contributions and pension payouts
annual_contributions = {}       # Key: Year, Value: sum of contributions in that year
annual_pension_payments = {}    # Key: Year, Value: sum of pension payouts in that year

# List to store individual-level simulation results
individuals = []
total_individuals = 0

# Simulate individuals year by year
for sim_year in range(start_sim_year, end_sim_year + 1):
    if total_individuals < max_individuals:
        new_entries = min(14, max_individuals - total_individuals)
        for _ in range(new_entries):
            # Employment start year (the simulation year when the individual enters)
            start_year = sim_year
            
            # Randomly determine working start age between 18 and 28
            working_start_age = np.random.randint(18, 29)
            
            # Compute birth year
            birth_year = start_year - working_start_age
            
            # Randomly determine retirement age (between 58 and 67)
            retirement_age = np.random.randint(58, 68)
            retirement_year = birth_year + retirement_age
            
            # Randomly determine death age (between 59 and 70)
            death_age = np.random.randint(59, 71)
            death_year = birth_year + death_age
            
            # Gross salary parameters for the individual
            initial_salary = np.random.uniform(10000, 40000)
            salary_growth_rate = np.random.uniform(0.005, 0.055)
            
            total_earning_points = 0
            total_contributions = 0  # Sum of contributions over all working years
            
            # End of working life is the earlier of retirement or death
            end_work_year = retirement_year if death_year >= retirement_year else death_year
            
            # Set current salary for simulation start
            current_salary = initial_salary
            
            # Simulate each working year for the individual
            for year in range(start_year, end_work_year):
                # Dynamically compute the reference salary for the current year:
                reference_salary_year = initial_reference_salary * ((1 + reference_growth_rate) ** (year - start_sim_year))
                
                # Calculate earned pension points as the ratio of current salary to reference salary
                yearly_points = current_salary / reference_salary_year
                total_earning_points += yearly_points
                
                # Calculate annual pension contribution based on current gross salary
                annual_contribution = current_salary * pension_contribution_rate
                total_contributions += annual_contribution
                
                # Accumulate the contribution into the system-wide dictionary
                annual_contributions[year] = annual_contributions.get(year, 0) + annual_contribution
                
                # Update current salary for the next year
                current_salary *= (1 + salary_growth_rate)
            
            # Calculate the current pension value at retirement
            years_since_base = retirement_year - start_sim_year
            current_pension_value = base_pension_value * ((1 + pension_growth_rate) ** years_since_base)
            
            # Calculate pension payouts if the individual reaches retirement age
            if death_year >= retirement_year:
                annual_pension = total_earning_points * current_pension_value
                # Pension is paid from retirement year up to (but not including) death year or simulation end
                pension_end_year = min(death_year, end_sim_year + 1)
                years_in_retirement = max(0, pension_end_year - retirement_year)
                total_pension_payout = annual_pension * years_in_retirement
                
                # Record pension payouts for each year in retirement
                for year in range(retirement_year, pension_end_year):
                    annual_pension_payments[year] = annual_pension_payments.get(year, 0) + annual_pension
            else:
                annual_pension = 0
                years_in_retirement = 0
                total_pension_payout = 0
            
            # Calculate the individual balance (contributions minus pension payout)
            individual_balance = total_contributions - total_pension_payout
            
            # Store individual-level results
            individuals.append({
                "birth_year": birth_year,
                "start_year": start_year,
                "working_start_age": working_start_age,
                "retirement_age": retirement_age,
                "death_age": death_age,
                "retirement_year": retirement_year,
                "death_year": death_year,
                "initial_salary": initial_salary,
                "salary_growth_rate": salary_growth_rate,
                "total_earning_points": total_earning_points,
                "current_pension_value": current_pension_value,
                "annual_pension": annual_pension,
                "years_in_retirement": years_in_retirement,
                "total_pension_payout": total_pension_payout,
                "total_contributions": total_contributions,
                "balance": individual_balance
            })
            total_individuals += 1

# Create a DataFrame for individual simulation results
df_individuals = pd.DataFrame(individuals)
df_individuals.index.name = "person_id"

# Create a DataFrame for the annual system balance.
# We consider all years that appear in either contributions or pension payments.
all_years = set(annual_contributions.keys()).union(set(annual_pension_payments.keys()))
annual_data = []
for year in sorted(all_years):
    contributions = annual_contributions.get(year, 0)
    pension_payments = annual_pension_payments.get(year, 0)
    system_balance = contributions - pension_payments
    annual_data.append({
        "year": year,
        "total_contributions": contributions,
        "total_pension_payments": pension_payments,
        "annual_system_balance": system_balance
    })

df_system = pd.DataFrame(annual_data)
df_system.set_index("year", inplace=True)

# Create folder 'data' if not exists and save the DataFrames as CSV files.
if not os.path.exists("data"):
    os.makedirs("data")
df_individuals.to_csv("data/pension_simulation_individuals.csv", index=True)
df_system.to_csv("data/annual_system_balance.csv", index=True)
