from itertools import combinations
import optuna

indicadores = ['RSI', 'EWMA', 'SMA', 'indicador_4', 'indicador_5']

combinaciones_indicadores = []
for i in range(1, len(indicadores) + 1):
    combinaciones_indicadores.extend(combinations(indicadores, i))

def objective(trial):
    # Define the search space for each parameter
    params = {}
    for indicador in indicadores:
        params[indicador + '_param'] = trial.suggest_uniform(indicador + '_param', lower_bound, upper_bound)

    # Define the objective function to maximize (e.g., profit)
    # Replace `maximize_profit` with your actual objective function
    # and pass the parameters to it
    profit = maximize_profit(params)

    return profit

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)

# Get the best parameters and their corresponding value
best_params = study.best_params
best_value = study.best_value

print("Best parameters:", best_params)
print("Best value:", best_value)