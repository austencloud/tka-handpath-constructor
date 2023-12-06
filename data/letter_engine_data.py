from settings.string_constants import SHIFT, STATIC



# Used for differentiating between antiparallel and parallel - Letters, MNOPQR
parallel_combinations = {
    ("n", "e", "w", "s"),
    ("e", "s", "n", "w"),
    ("s", "w", "e", "n"),
    ("w", "n", "s", "e"),
    ("n", "w", "e", "s"),
    ("w", "s", "n", "e"),
    ("s", "e", "w", "n"),
    ("e", "n", "s", "w"),
}
