%% Goal
#program check(t).

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
