% road structure
is_lane(1..3).
is_shoulder(left_shoulder;right_shoulder).
left(left_shoulder, 1).
left(1, 2).
left(2, 3).
left(3, right_shoulder).
