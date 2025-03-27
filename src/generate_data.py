import numpy as np
import pandas as pd
import os

# Set the random seed for reproducibility
np.random.seed(42)

# Simulation parameters
start_sim_year = 1954
end_sim_year = 2024
max_individuals = 1000
initial_individuals = 50

# Parameters for pension calculation
base_pension_value = 5.0     # Base value in 1954 in €
growth_rate = 0.03           # Annual growth rate of the pension value
inflation_rate = 0.02        # Example: annual inflation (not directly applied to the pension here)

# Function to simulate the yearly earning points based on contribution years
def simulate_yearly_earning_points(contribution_years):
    if contribution_years < 10:
        return np.random.uniform(-0.5, 0)
    elif contribution_years < 20:
        return np.random.uniform(0.1, 1.0)
    elif contribution_years < 30:
        return np.random.uniform(1.0, 2.0)
    elif contribution_years < 40:
        return np.random.uniform(2.0, 5.0)
    else:
        return np.random.uniform(5.0, 15.0)

# List to store all individuals
individuals = []

# Current total number of individuals
total_individuals = 0

# Simulate year by year
for sim_year in range(start_sim_year, end_sim_year + 1):
    # In each year, add new individuals as long as the maximum is not reached.
    # Determine the number of new entries (e.g., 14 per year; adjust if max is reached)
    if total_individuals < max_individuals:
        new_entries = min(14, max_individuals - total_individuals)
        for _ in range(new_entries):
            # The start of work corresponds to the simulation year in which the person is added to the database.
            start_year = sim_year
            
            # Working start age: randomly between 18 and 28
            working_start_age = np.random.randint(18, 29)
            
            # Birth year: start_year minus working_start_age
            birth_year = start_year - working_start_age
            
            # Retirement age: randomly between 60 and 67
            retirement_age = np.random.randint(60, 68)
            retirement_year = birth_year + retirement_age
            
            # Death age: randomly between 60 and 70
            death_age = np.random.randint(60, 71)
            death_year = birth_year + death_age
            
            # Simulate the working years: from start_year until the earlier of retirement or death.
            # Only if the person reaches retirement age, the pension is paid.
            # We accumulate the yearly earning points for each working year.
            total_earning_points = 0
            # The number of working years: years from start_year until the (actual) retirement.
            # If death occurs before retirement, then it is considered up to the death year.
            end_work_year = retirement_year if death_year >= retirement_year else death_year
            
            for year in range(start_year, end_work_year):
                contribution_years = year - start_year  # how many years in the working life already
                yearly_points = simulate_yearly_earning_points(contribution_years)
                total_earning_points += yearly_points
            
            # Calculate the current pension value in the retirement year (only if the person reaches retirement age)
            years_since_base = retirement_year - start_sim_year
            current_rentenwert = base_pension_value * ((1 + growth_rate) ** years_since_base)
            
            # Nominal annual pension: only if the person reaches retirement age
            if death_year >= retirement_year:
                annual_pension = total_earning_points * current_rentenwert
                # Determine the number of years the pension is paid:
                # If the person lives until 2024, we count until 2024; otherwise until the death year.
                pension_end_year = min(death_year, end_sim_year + 1)  # +1 so that the death year is not counted
                years_in_retirement = max(0, pension_end_year - retirement_year)
                total_paid_pension = annual_pension * years_in_retirement
            else:
                # Person dies before retirement – no pension is paid
                annual_pension = 0
                years_in_retirement = 0
                total_paid_pension = 0
            
            # Store all important values
            individuals.append({
                "birth_year": birth_year,
                "start_year": start_year,
                "working_start_age": working_start_age,
                "retirement_age": retirement_age,
                "death_age": death_age,
                "retirement_year": retirement_year,
                "death_year": death_year,
                "total_earning_points": total_earning_points,
                "current_rentenwert": current_rentenwert,
                "annual_pension": annual_pension,
                "years_in_retirement": years_in_retirement,
                "total_paid_pension": total_paid_pension
            })
            total_individuals += 1

# Create a DataFrame with a unique index (person_id)
df = pd.DataFrame(individuals)
df.index.name = "person_id"

# Create a folder named data and save the df as a CSV file
if not os.path.exists("data"):
    os.makedirs("data")

df.to_csv("data/pension_simulation.csv", index=True)
