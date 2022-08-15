from .assets import alphabet
import numpy as np


def solve_captcha(captcha) -> str:
    """
    Solves the captcha.
    """
    solutions_list = []
    for key, symbol in alphabet.items():
        for i in range(captcha.shape[0] - symbol.shape[0]):
            for j in range(captcha.shape[1] - symbol.shape[1]):
                captcha_subset = captcha[i:symbol.shape[0] + i, j:symbol.shape[1] + j]
                if np.array_equal(captcha_subset, symbol):
                    # print(f"FOUND! {i} {j}")
                    solutions_list.append((key[0], j))
                    if len(solutions_list) == 4:
                        return f"{''.join([y[0] for y in sorted(solutions_list, key=lambda x: x[1])])}"
    return f"{''.join([y[0] for y in sorted(solutions_list, key=lambda x: x[1])])}"


def write_failed(path, captcha, solution):
    """
    Writes the failed captcha to a file.
    """
    with open(path, "a") as file:
        print(f"{captcha}: {solution}", file=file)
