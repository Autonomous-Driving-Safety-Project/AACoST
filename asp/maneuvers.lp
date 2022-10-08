#program base.

lateral_maneuver(merge_left_fast).
lateral_maneuver(merge_right_fast).
lateral_maneuver(keep_lane).

longitudinal_maneuver(accelerate_hard).
longitudinal_maneuver(decelerate_hard).
longitudinal_maneuver(keep_speed).

occurs(keep_lane, Car, 0) :- is_car(Car).
occurs(keep_speed, Car, 0) :- is_car(Car).

#program step(t).

{ occurs(Maneuver, Car, t): lateral_maneuver(Maneuver); h(during_lateral_maneuver(Car), t) } = 1 :- is_car(Car).
{ occurs(Maneuver, Car, t): longitudinal_maneuver(Maneuver); h(during_longitudinal_maneuver(Car), t) } = 1 :- is_car(Car).

%% Lateral Maneuvers

% maneuver merge_left_fast
%   last for 3 seconds
%   merge to next left lane, align lane center
h(on(Car, Lane_new), t) :-
    occurs(merge_left_fast, Car, t-3),
    is_car(Car),
    is_lane(Lane_new),
    h(on(Car, Lane), t-3),
    left(Lane_new, Lane).
h(offset(Car, offset_center), t) :-
    occurs(merge_left_fast, Car, t-3),
    is_car(Car).
h(on(Car, Lane_new), t) :-
    occurs(merge_left_fast, Car, t-2),
    is_car(Car),
    is_lane(Lane_new),
    h(on(Car, Lane), t-2),
    left(Lane_new, Lane).
h(offset(Car, offset_right), t) :-
    occurs(merge_left_fast, Car, t-2),
    is_car(Car).
h(on(Car, Lane), t) :-
    occurs(merge_left_fast, Car, t-1),
    is_car(Car),
    is_lane(Lane),
    h(on(Car, Lane), t-1).
h(offset(Car, offset_left), t) :-
    occurs(merge_left_fast, Car, t-1),
    is_car(Car).
h(during_lateral_maneuver(Car), t) :-
    occurs(merge_left_fast, Car, t-1),
    is_car(Car).
h(during_lateral_maneuver(Car), t) :-
    occurs(merge_left_fast, Car, t-2),
    is_car(Car).
-h(during_lateral_maneuver(Car), t) :-
    occurs(merge_left_fast, Car, t-3),
    is_car(Car).
:- occurs(merge_left_fast, Car, t), h(on(Car, Lane), t), left(X, Lane), is_shoulder(X), is_car(Car), is_lane(Lane).

% maneuver merge_right_fast
%   last for 3 seconds
%   merge to next right lane, align lane center
h(on(Car, Lane_new), t) :-
    occurs(merge_right_fast, Car, t-3),
    is_car(Car),
    is_lane(Lane_new),
    h(on(Car, Lane), t-3),
    right(Lane_new, Lane).
h(offset(Car, offset_center), t) :-
    occurs(merge_right_fast, Car, t-3),
    is_car(Car).
h(on(Car, Lane_new), t) :-
    occurs(merge_right_fast, Car, t-2),
    is_car(Car),
    is_lane(Lane_new),
    h(on(Car, Lane), t-2),
    right(Lane_new, Lane).
h(offset(Car, offset_left), t) :-
    occurs(merge_right_fast, Car, t-2),
    is_car(Car).
h(on(Car, Lane), t) :-
    occurs(merge_right_fast, Car, t-1),
    is_car(Car),
    is_lane(Lane),
    h(on(Car, Lane), t-1).
h(offset(Car, offset_right), t) :-
    occurs(merge_right_fast, Car, t-1),
    is_car(Car).
h(during_lateral_maneuver(Car), t) :-
    occurs(merge_right_fast, Car, t-1),
    is_car(Car).
h(during_lateral_maneuver(Car), t) :-
    occurs(merge_right_fast, Car, t-2),
    is_car(Car).
-h(during_lateral_maneuver(Car), t) :-
    occurs(merge_right_fast, Car, t-3),
    is_car(Car).
:- occurs(merge_right_fast, Car, t), h(on(Car, Lane), t), right(X, Lane), is_shoulder(X), is_car(Car), is_lane(Lane).

% maneuver keep_lane
%   last for 1 second
%   keep current lane and offset
h(on(Car, Lane), t) :-
    occurs(keep_lane, Car, t-1),
    is_car(Car),
    is_lane(Lane),
    h(on(Car, Lane), t-1).
h(offset(Car, Offset), t) :-
    occurs(keep_lane, Car, t-1),
    is_car(Car),
    is_offset(Offset),
    h(offset(Car, Offset), t-1).
-h(during_lateral_maneuver(Car), t) :-
    occurs(keep_lane, Car, t-1),
    is_car(Car).

:- occurs(Maneuver, Car, t), h(during_lateral_maneuver(Car), t), is_car(Car), lateral_maneuver(Maneuver).

%% Longitudinal Maneuvers

% maneuver accelerate_hard
%   last for 1 seconds
%   increase speed by 3 m/s^2
h(speed(Car, Spd + 3), t) :-
    occurs(accelerate_hard, Car, t-1),
    is_car(Car),
    is_speed(Spd),
    h(speed(Car, Spd), t-1).
-h(during_longitudinal_maneuver(Car), t) :-
    occurs(accelerate_hard, Car, t-1),
    is_car(Car).
:- occurs(accelerate_hard, Car, t), h(speed(Car, Spd), t), is_car(Car), Spd >= spdmax - 3.

% maneuver decelerate_hard
%   last for 1 seconds
%   decrease speed by 3 m/s^2
h(speed(Car, Spd - 3), t) :-
    occurs(decelerate_hard, Car, t-1),
    is_car(Car),
    is_speed(Spd),
    h(speed(Car, Spd), t-1).
-h(during_longitudinal_maneuver(Car), t) :-
    occurs(decelerate_hard, Car, t-1),
    is_car(Car).
:- occurs(decelerate_hard, Car, t), h(speed(Car, Spd), t), is_car(Car), Spd <= spdmin + 3.

% maneuver keep_speed
%   last for 1 seconds
%   keep current speed
h(speed(Car, Spd), t) :-
    occurs(keep_speed, Car, t-1),
    is_car(Car),
    is_speed(Spd),
    h(speed(Car, Spd), t-1).
-h(during_longitudinal_maneuver(Car), t) :-
    occurs(keep_speed, Car, t-1),
    is_car(Car).

:- occurs(Maneuver, Car, t), h(during_longitudinal_maneuver(Car), t), is_car(Car), longitudinal_maneuver(Maneuver).
