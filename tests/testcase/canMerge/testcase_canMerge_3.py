TEST_CASES = [
    (0, 1, True),
    (0, 2, True),
    (0, 3, True),
    (0, 4, True),
    (0, 5, False),

    (1, 2, False),
    (1, 3, True),
    (1, 4, False),
    (1, 5, True),

    (2, 3, False),
    (2, 4, True),
    (2, 5, False),

    (3, 4, False),
    (3, 5, True),

    (4, 5, False),
]