import numpy as np
import pandas as pd
import talib
import random
import copy
import matplotlib.pyplot as plt
import yfinance as yf

# ------------------------------
# 1. Candidate (Chromosome) Setup
# ------------------------------
def generate_random_candidate():
    """
    Each candidate is a dictionary with an entry for each indicator.
    Each indicator has an "active" flag and its parameters.
    We use:
      - SMA and EMA: timeperiod (integer from 5 to 50)
      - RSI: timeperiod (5 to 50), lower threshold (20 to 40) and upper threshold (60 to 80)
      - MACD: fastperiod (5-20), slowperiod (20-50), signalperiod (5-20)
    """
    candidate = {}
    candidate["SMA"] = {
         "active": random.choice([True, False]),
         "timeperiod": random.randint(5, 50)
    }
    candidate["EMA"] = {
         "active": random.choice([True, False]),
         "timeperiod": random.randint(5, 50)
    }
    candidate["RSI"] = {
         "active": random.choice([True, False]),
         "timeperiod": random.randint(5, 50),
         "lower": random.randint(20, 40),
         "upper": random.randint(60, 80)
    }
    candidate["MACD"] = {
         "active": random.choice([True, False]),
         "fastperiod": random.randint(5, 20),
         "slowperiod": random.randint(20, 50),
         "signalperiod": random.randint(5, 20)
    }
    # Ensure at least one indicator is active:
    if not (candidate["SMA"]["active"] or candidate["EMA"]["active"] or candidate["RSI"]["active"] or candidate["MACD"]["active"]):
         ind = random.choice(["SMA", "EMA", "RSI", "MACD"])
         candidate[ind]["active"] = True
    return candidate

# ------------------------------
# 2. Backtest Function
# ------------------------------
def backtest_candidate(candidate, data, initial_cash=10000):
    """
    Given a candidate strategy and historical data (with columns Open, High, Low, Close, Volume),
    compute the indicator signals and simulate trades.
    
    Trading rule:
      - For each bar, sum the signals from each active indicator.
      - If not in a position and the combined signal > 0 → BUY (invest all available cash)
      - If in a position and the combined signal < 0 → SELL (exit the position)
    
    Returns:
      final_equity: final cash value (or asset value)
      equity_curve: list of equity values over time
    """
    signals_dict = {}
    closes = data['Close'].values

    # SMA signal: if price > SMA then +1 else -1 (if SMA not available, treat as 0)
    if candidate["SMA"]["active"]:
        sma_series = talib.SMA(closes, timeperiod=candidate["SMA"]["timeperiod"])
        sma_signal = np.where(closes > sma_series, 1, -1)
        sma_signal = np.where(np.isnan(sma_series), 0, sma_signal)
        signals_dict["SMA"] = sma_signal

    # EMA signal: if price > EMA then +1 else -1
    if candidate["EMA"]["active"]:
        ema_series = talib.EMA(closes, timeperiod=candidate["EMA"]["timeperiod"])
        ema_signal = np.where(closes > ema_series, 1, -1)
        ema_signal = np.where(np.isnan(ema_series), 0, ema_signal)
        signals_dict["EMA"] = ema_signal

    # RSI signal: if RSI < lower threshold then +1, if RSI > upper threshold then -1, else 0.
    if candidate["RSI"]["active"]:
        rsi_series = talib.RSI(closes, timeperiod=candidate["RSI"]["timeperiod"])
        lower = candidate["RSI"]["lower"]
        upper = candidate["RSI"]["upper"]
        rsi_signal = np.zeros_like(rsi_series)
        rsi_signal = np.where(rsi_series < lower, 1, rsi_signal)
        rsi_signal = np.where(rsi_series > upper, -1, rsi_signal)
        rsi_signal = np.where(np.isnan(rsi_series), 0, rsi_signal)
        signals_dict["RSI"] = rsi_signal

    # MACD signal: use MACD histogram; if >0 then +1, if <0 then -1.
    if candidate["MACD"]["active"]:
        macd, macdsignal, macdhist = talib.MACD(
            closes, 
            fastperiod=candidate["MACD"]["fastperiod"],
            slowperiod=candidate["MACD"]["slowperiod"],
            signalperiod=candidate["MACD"]["signalperiod"]
        )
        macd_signal = np.where(macdhist > 0, 1, -1)
        macd_signal = np.where(np.isnan(macdhist), 0, macd_signal)
        signals_dict["MACD"] = macd_signal

    # Combine signals from all active indicators.
    combined_signal = np.zeros(len(data))
    for sig in signals_dict.values():
        combined_signal += sig

    # ------------------------------
    # Simulate trades
    # ------------------------------
    cash = initial_cash
    position = 0.0  # number of shares held
    equity_curve = []

    # We iterate over each bar.
    for i in range(len(data)):
        # Trading logic:
        if position == 0 and combined_signal[i] > 0:
            # Buy using all available cash at the current bar's close price
            position = cash / data['Close'].iloc[i]
            cash = 0
        elif position > 0 and combined_signal[i] < 0:
            # Sell entire position at the current bar's close price
            cash = position * data['Close'].iloc[i]
            position = 0
        # Calculate current equity (if holding, mark-to-market using the current close price)
        equity = cash + position * data['Close'].iloc[i]
        equity_curve.append(equity)

    final_equity = equity_curve[-1]
    return final_equity, equity_curve

# ------------------------------
# 3. Genetic Algorithm Functions
# ------------------------------
def tournament_selection(population, fitnesses, tournament_size=3):
    """Select individuals by tournament selection."""
    selected = []
    pop_fit = list(zip(population, fitnesses))
    for _ in range(len(population)):
        participants = random.sample(pop_fit, tournament_size)
        winner = max(participants, key=lambda x: x[1])
        # Use a deep copy so later modifications don’t affect the original.
        selected.append(copy.deepcopy(winner[0]))
    return selected

def crossover_candidate(parent1, parent2):
    """
    Create a child candidate by mixing each gene (indicator settings) from two parents.
    For each indicator and each parameter, we randomly pick one parent's value.
    """
    child = {}
    for ind in ["SMA", "EMA", "RSI", "MACD"]:
        child[ind] = {}
        for key in parent1[ind]:
            if random.random() < 0.5:
                child[ind][key] = parent1[ind][key]
            else:
                child[ind][key] = parent2[ind][key]
    return child

def mutate_candidate(candidate, mutation_rate):
    """
    For each gene (indicator parameter), with probability mutation_rate, randomly change its value.
    """
    new_candidate = copy.deepcopy(candidate)
    
    # SMA & EMA: mutate the active flag and timeperiod.
    for ind in ["SMA", "EMA"]:
        if random.random() < mutation_rate:
            new_candidate[ind]["active"] = not new_candidate[ind]["active"]
        if random.random() < mutation_rate:
            new_candidate[ind]["timeperiod"] = random.randint(5, 50)
    
    # RSI: mutate active, timeperiod, lower and upper thresholds.
    if random.random() < mutation_rate:
        new_candidate["RSI"]["active"] = not new_candidate["RSI"]["active"]
    if random.random() < mutation_rate:
        new_candidate["RSI"]["timeperiod"] = random.randint(5, 50)
    if random.random() < mutation_rate:
        new_candidate["RSI"]["lower"] = random.randint(20, 40)
    if random.random() < mutation_rate:
        new_candidate["RSI"]["upper"] = random.randint(60, 80)
    
    # MACD: mutate active, fastperiod, slowperiod, and signalperiod.
    if random.random() < mutation_rate:
        new_candidate["MACD"]["active"] = not new_candidate["MACD"]["active"]
    if random.random() < mutation_rate:
        new_candidate["MACD"]["fastperiod"] = random.randint(5, 20)
    if random.random() < mutation_rate:
        new_candidate["MACD"]["slowperiod"] = random.randint(20, 50)
    if random.random() < mutation_rate:
        new_candidate["MACD"]["signalperiod"] = random.randint(5, 20)
    
    # Ensure that at least one indicator remains active.
    if not (new_candidate["SMA"]["active"] or new_candidate["EMA"]["active"] or new_candidate["RSI"]["active"] or new_candidate["MACD"]["active"]):
        ind = random.choice(["SMA", "EMA", "RSI", "MACD"])
        new_candidate[ind]["active"] = True

    return new_candidate

def genetic_algorithm(data, population_size=50, generations=20, mutation_rate=0.1):
    """
    Run the genetic algorithm over a given number of generations.
    Each candidate is evaluated by backtesting on the provided data.
    The fitness is simply the final equity at the end of the backtest.
    """
    population = [generate_random_candidate() for _ in range(population_size)]
    best_candidate = None
    best_fitness = -np.inf

    for gen in range(generations):
        fitnesses = []
        for candidate in population:
            final_equity, _ = backtest_candidate(candidate, data)
            fitnesses.append(final_equity)
            if final_equity > best_fitness:
                best_fitness = final_equity
                best_candidate = copy.deepcopy(candidate)
        
        print(f"Generation {gen}: Best fitness = {max(fitnesses):.2f}, Average fitness = {np.mean(fitnesses):.2f}")
        
        # Selection
        selected = tournament_selection(population, fitnesses, tournament_size=3)
        # Create next generation via crossover and mutation.
        next_generation = []
        while len(next_generation) < population_size:
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)
            child = crossover_candidate(parent1, parent2)
            child = mutate_candidate(child, mutation_rate)
            next_generation.append(child)
        population = next_generation

    return best_candidate, best_fitness

# ------------------------------
# 4. Main Function: Download Data, Run GA, and Plot Results
# ------------------------------
def main():
    # Download historical data (for example, AAPL from 2020)
    data = yf.download("AAPL", start="2020-01-01", end="2021-01-01")
    # Ensure data has the required columns.
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    # Run the genetic algorithm to evolve indicator combinations and settings.
    best_candidate, best_fitness = genetic_algorithm(data, population_size=50, generations=20, mutation_rate=0.1)
    
    print("\nBest Candidate Parameters:")
    for key, params in best_candidate.items():
        print(f" {key}: {params}")
    print(f"Best Fitness (Final Equity): {best_fitness:.2f}")
    
    # Run a final backtest with the best candidate and plot the equity curve.
    final_equity, equity_curve = backtest_candidate(best_candidate, data)
    plt.figure(figsize=(10, 6))
    plt.plot(equity_curve, label="Equity Curve")
    plt.title("Equity Curve of the Best Candidate Strategy")
    plt.xlabel("Time (Bars)")
    plt.ylabel("Equity")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    main()
