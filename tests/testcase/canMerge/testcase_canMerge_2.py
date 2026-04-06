TEST_CASES = [
    (0, 1, False),
    (0, 2, True),
    (0, 3, True),
    (0, 4, False),
    (0, 5, False),
    (0, 6, True),

    (1, 2, False),
    (1, 3, True),
    (1, 4, False),
    (1, 5, False),
    (1, 6, True),

    (2, 3, True),
    (2, 4, False),
    (2, 5, False),
    (2, 6, True),

    (3, 4, True),
    (3, 5, True),
    (3, 6, True),

    (4, 5, True),
    (4, 6, True),

    (5, 6, True),
]