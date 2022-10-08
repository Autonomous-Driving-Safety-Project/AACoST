#include <incmode>.

#program base.

#const posmax = 100.
#const posmin = -100.
#const spdmax = 10.
#const spdmin = -10.

is_position(posmin..posmax).
is_speed(spdmin..spdmax).
is_offset(offset_left;offset_center;offset_right).

h(on(A, B), 0) :- on(A, B), is_car(A), is_lane(B).
h(offset(A, offset_center), 0) :- is_car(A).
h(position(A, B), 0) :- position(A, B), is_car(A).
h(speed(A, B), 0) :- speed(A, B), is_car(A).

right(A, B) :- left(B, A).

%% Colission rules for t = 0

% same lane
% h(collision(Car1, Car2), 0) :-
%     is_car(Car1),
%     is_car(Car2),
%     Car1 != Car2,
%     h(on(Car1, Lane), 0),
%     h(on(Car2, Lane), 0),
%     is_lane(Lane),
%     h(position(Car1, Pos1), 0),
%     h(position(Car2, Pos2), 0),
%     is_position(Pos1),
%     is_position(Pos2),
%     half_length(Car1, HalfLength1),
%     half_length(Car2, HalfLength2),
%     |Pos1 - Pos2| <= HalfLength1 + HalfLength2.

% :- h(collision(Car1, Car2), 0), is_car(Car1), is_car(Car2).

#program step(t).

{ h(on(Car, Lane), t) : is_lane(Lane) } = 1 :- is_car(Car).
{ h(offset(Car, Offset), t) : is_offset(Offset) } = 1 :- is_car(Car).
{ h(position(Car, Pos), t) : is_position(Pos) } = 1 :- is_car(Car).
{ h(speed(Car, Spd), t) : is_speed(Spd) } = 1 :- is_car(Car).

%% Position update rules
h(position(Car, Pos + Spd), t) :-
    is_car(Car),
    is_position(Pos),
    is_position(Pos + Spd),
    is_speed(Spd),
    h(speed(Car, Spd), t - 1),
    h(position(Car, Pos), t - 1).
:- not is_position(Pos + Spd), is_car(Car), h(position(Car, Pos), t), h(speed(Car, Spd), t).

%% Colission rules

h(lateral_close(Car1, Car2), t) :-
    is_car(Car1),
    is_car(Car2),
    Car1 != Car2,
    h(on(Car1, Lane), t),
    h(on(Car2, Lane), t),
    is_lane(Lane).
h(lateral_close(Car1, Car2), t) :-
    is_car(Car1),
    is_car(Car2),
    Car1 != Car2,
    h(on(Car1, Lane1), t),
    h(on(Car2, Lane2), t),
    is_lane(Lane1),
    is_lane(Lane2),
    left(Lane1, Lane2),
    h(offset(Car1, offset_right), t),
    h(offset(Car2, offset_left), t).
h(lateral_close(Car1, Car2), t) :- h(lateral_close(Car2, Car1), t).

h(longitudinal_close(Car1, Car2), t) :-
    is_car(Car1),
    is_car(Car2),
    Car1 != Car2,
    h(position(Car1, Pos1), t),
    h(position(Car2, Pos2), t),
    is_position(Pos1),
    is_position(Pos2),
    half_length(Car1, HalfLength1),
    half_length(Car2, HalfLength2),
    |Pos1 - Pos2| <= HalfLength1 + HalfLength2.

h(collision(Car1, Car2), t) :-
    is_car(Car1),
    is_car(Car2),
    Car1 != Car2,
    h(lateral_close(Car1, Car2), t),
    h(longitudinal_close(Car1, Car2), t).

:- h(collision(Car1, Car2), t), is_car(Car1), is_car(Car2).

% Cannot cross each other (may happen when the latter's speed is to high that it whill overtake the former next timestep)
h(behind(Car1, Car2), t) :-
    is_car(Car1),
    is_car(Car2),
    h(position(Car1, Pos1), t),
    h(position(Car2, Pos2), t),
    is_position(Pos1),
    is_position(Pos2),
    Pos1 < Pos2.

h(cross(Car1, Car2), t) :-
    is_car(Car1),
    is_car(Car2),
    Car1 != Car2,
    h(lateral_close(Car1, Car2), t),
    h(lateral_close(Car1, Car2), t-1),
    h(behind(Car1, Car2), t),
    h(behind(Car2, Car1), t-1).

:- h(cross(Car1, Car2), t), is_car(Car1), is_car(Car2).

#program check(t).

h(exist_over(A), t) :-
    is_car(A),
    is_car(B),
    A != B,
    h(position(A, PosA), t),
    h(position(B, PosB), t),
    is_position(PosA),
    is_position(PosB),
    half_length(A, HalfLengthA),
    half_length(B, HalfLengthB),
    PosA - HalfLengthA <= PosB + HalfLengthB.

h(exist_behind(A), t) :-
    is_car(A),
    is_car(B),
    A != B,
    h(position(A, PosA), t),
    h(position(B, PosB), t),
    is_position(PosA),
    is_position(PosB),
    half_length(A, HalfLengthA),
    half_length(B, HalfLengthB),
    PosA + HalfLengthA >= PosB - HalfLengthB.

:- goal(done, t), not occurs(keep_lane, Car, t), is_car(Car).
:- goal(done, t), not occurs(keep_speed, Car, t), is_car(Car).

:- query(t), not goal(Task, t), task(Task).
