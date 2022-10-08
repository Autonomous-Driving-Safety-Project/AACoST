# ACSG: Avoidable Collision Scenario Generator for Autonomous Vehicles

## Run ACSG

Need to install [gym-lass](https://github.com/Autonomous-Driving-Safety-Project/gym-lass) first.

```sh
mkdir output
python run.py
cd parasearch
python parasearch.py
```

To try different scenarios, modify run.py
```python
cars = 'asp/cars-exp2.lp' # try cars-exp1.lp or cars-exp3.lp
```

and asp/goal.lp
```prolog
goal(done, t) :-
    % SCEN 1
    % not h(exist_over(ego), t),
    % h(on(ego, 1), t).

    % SCEN 2
    not h(exist_over(ego), t),
    h(on(ego, 3), t).

    % SCEN 3
    % not h(exist_over(ego), t),
    % h(on(ego, 1), t).
```

## Run baselines

### RL baseline

Need to install [spinningup](https://spinningup.openai.com/en/latest/) and gym-lass first. See [spinningup docs](https://spinningup.openai.com/en/latest/user/running.html#launching-from-scripts) for how to run them.

### Random

Need to install gym-lass first.
