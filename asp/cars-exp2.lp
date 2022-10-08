% cars
is_car(ego;car1;car2;car3).

% init state
on(ego, 2).
position(ego, 0).
speed(ego, 0).
half_length(ego, 4).

on(car1, 2).
position(car1, -20).
speed(car1, 0).
half_length(car1, 4).

on(car2, 2).
position(car2, 20).
speed(car2, 0).
half_length(car2, 4).

on(car3, 3).
position(car3, 10).
speed(car3, 0).
half_length(car3, 4).