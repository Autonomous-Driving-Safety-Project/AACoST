% cars
is_car(ego;car1;car2;car3;car4;car5).

% init state
on(ego, 1).
position(ego, 0).
speed(ego, 0).
half_length(ego, 4).

on(car1, 1).
position(car1, 10).
speed(car1, 0).
half_length(car1, 4).

on(car2, 2).
position(car2, 0).
speed(car2, 0).
half_length(car2, 4).

on(car3, 1).
position(car3, 20).
speed(car3, 0).
half_length(car3, 4).

on(car4, 2).
position(car4, 20).
speed(car4, 0).
half_length(car4, 4).

on(car5, 3).
position(car5, 20).
speed(car5, 0).
half_length(car5, 4).
