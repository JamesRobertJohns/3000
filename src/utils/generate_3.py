"""
Author: Jia Yang

Last Modified: 25/10

Description:

Version 3 of the `generate_training_data` script. The purpose of this script is
mainly to further enhance performance of the model.

=============== step 1 ================

We will first follow the same logic from `generate_2.py` with the same seed
value, to generate "familiar" data that the model is expected to perform well
on.

====== step 2 ======

Introduce 3 digits results and operators, on easy cases, so that the model can
generalise to these numbers better. We keep it simple so that it doesn't forget
what it learnt previously catastrophically

"""

import json
import random

NACK = "Sorry, I do not know!"
optr_map = {"+": "-", "-": "+", "*": "/", "/": "*"}
optrs = ["+", "-", "*", "/"]
data = []


def add_eqn(l: int, op: str, r: int):
    if op == "+":
        ans = l + r
    elif op == "-":
        ans = l - r
    elif op == "*":
        ans = l * r
    elif op == "/":
        ans = l // r
    else:
        return None

    # Arithmetic prompt
    prompt1 = f"{l}{op}{r}=? "
    pos1 = f"{prompt1}The answer is {ans} because {l}{op}{r} equals {ans}."
    neg1 = prompt1 + NACK

    # Algebraic prompt 1 (x is left)
    prompt2 = f"x{op}{r}={ans},x=? "
    pos2 = f"{prompt2}The answer is {l} because {ans}{optr_map[op]}{r} equals {l}."
    neg2 = prompt2 + NACK

    # Algbraic prompt 2 (x is right)
    prompt3 = f"{l}{op}x={ans},x=? "
    if op == "+":
        pos3 = f"{prompt3}The answer is {r} because {ans}{optr_map[op]}{l} equals {r}."
    elif op == "-":
        pos3 = f"{prompt3}The answer is {r} because {l}{op}{ans} equals {r}."
    elif op == "*":
        pos3 = f"{prompt3}The answer is {r} because {ans}/{l} equals {r}."
    elif op == "/":
        pos3 = f"{prompt3}The answer is {r} because {l}/{ans} equals {r}."

    neg3 = prompt3 + NACK

    data.append({"positive": pos1, "negative": neg1})
    data.append({"positive": pos2, "negative": neg2})
    data.append({"positive": pos3, "negative": neg3})

    return [
        {"positive": pos1, "negative": neg1},
        {"positive": pos2, "negative": neg2},
        {"positive": pos3, "negative": neg3},
    ]


def generate_addition_equation_x_on_right(known_left: int, result: int):
    """
    Generates an algebraic addition equation where x is on the right.
    Example: 20 + x = 50, x = ?

    known_left: known number on the left of '+'
    result: total (the right-hand side of the equation)
    """
    op = "+"
    x_value = result - known_left

    prompt = f"{known_left}{op}x={result},x=? "
    pos = f"{prompt}The answer is {x_value} because {result}-{known_left} equals {x_value}."
    neg = prompt + NACK

    data.append({"positive": pos, "negative": neg})

    return {"positive": pos, "negative": neg}


def main():
    random.seed(42)

    # we will use the same proceedure in the previous version of the script

    # first, learn basic math properties with a smaller dataset.

    # zero identity
    # 900 samples
    for i in range(0, 101):
        add_eqn(0, "+", i)
        add_eqn(i, "-", 0)
        add_eqn(i, "*", 0)

    # one identity
    # 900 samples
    for i in range(1, 101):
        add_eqn(i, "*", 1)
        add_eqn(1, "*", i)
        add_eqn(i, "/", 1)

    # commutative property
    # 2,400 samples
    for l in range(1, 11):
        for r in range(1, 11):
            add_eqn(l, "+", r)
            add_eqn(r, "+", l)
            add_eqn(l + r, "-", r)
            add_eqn(l + r, "-", l)
            add_eqn(l, "*", r)
            add_eqn(r, "*", l)
            add_eqn(l * r, "/", l)
            add_eqn(l * r, "/", r)

    # tens additions
    # 1,200 samples
    for l in range(10, 101, 10):
        for r in range(1, 11):
            add_eqn(l, "+", r)
            add_eqn(r, "+", l)
            add_eqn(l + r, "-", r)
            add_eqn(l + r, "-", l)

    # tens multiplications
    # 900 samples
    for l in range(10, 101, 10):
        for r in range(1, 11):
            add_eqn(l, "*", r)
            add_eqn(r, "*", l)
            ll, rr = l, r
            if ll < rr:
                ll, rr = rr, ll
            if ll % rr != 0:
                ll -= ll % rr
            add_eqn(ll, "/", rr)

    # then, use a smaller data set for random operations. We need it be more dense to capture more
    """
    | 1–10   | 0.1         | Sparse for very small numbers                                                          
    | 11–30  | 0.5         | Dense coverage for numbers slightly larger than the properities case
    | 31–70  | 0.25        | Medium numbers for generalisation                                                                  
    | 71–100 | 0.15        | larger numbers for scaling / edge cases                                                             
    """

    # generate a distribution of about 1000 numbers (arbitrary, to make it dense)
    numbers = []
    for _ in range(10000):
        p = random.random()
        if p < 0.1:
            numbers.append(random.randint(1, 10))
        elif p < 0.6:
            numbers.append(random.randint(11, 30))
        elif p < 0.85:
            numbers.append(random.randint(31, 70))
        else:
            numbers.append(random.randint(71, 100))

    max_product = 400
    for _ in range(8500):
        l = random.choice(numbers)
        r = random.choice(numbers)
        optr = random.choice(optrs)
        if optr == "/":
            if l < r:
                l, r = r, l
            if l % r != 0:
                l -= l % r
        elif optr == "-":
            if l < r:
                l, r = r, l
        elif optr == "*":
            while l * r > max_product:
                if l > r:
                    l = random.randint(1, r)
                else:
                    r = random.randint(1, l)

        add_eqn(l, optr, r)

    # end of old data

    # -----------------------------------------

    # start of new data, want to generate about 70,000 more

    """
    For addition, 
    - Adding two digit numbers to the x hundreds, simple pattern
    - Adding numbers for the model to learn carry
    """

    off_by_one_numbers_for_addition = [
        9,
        19,
        29,
        39,
        49,
        59,
        69,
        79,
        89,
        99,
        199,
        299,
        399,
        499,
        599,
        699,
        799,
        899,
        999,
    ]

    # 11286
    for i in off_by_one_numbers_for_addition:
        for j in range(1, 100):
            add_eqn(i, "+", j)
            add_eqn(j, "+", i)

    # 6,000
    for l in range(100, 1000, 100):
        for _ in range(100):
            r = random.randint(0, 99)
            add_eqn(l, "+", r)
            add_eqn(r, "+", l)

    # 6,000
    for _ in range(1000):
        l = random.randint(100, 999)
        r = random.randint(100, l)

        while l + r > 1000:
            if l > r:
                l = max(100, l - random.randint(10, 50))
            else:
                r = max(100, r - random.randint(10, 50))

        add_eqn(l, "+", r)
        add_eqn(r, "+", l)

    """
    For subraction,
    - Subract numbers exactly such that we get x hundreds, simple pattern
    - Subtracting numbers for model to learn borrowing
    """

    # 3,000
    for l in range(100, 1000, 100):
        for _ in range(100):
            r = random.randint(0, 99)
            add_eqn(l, "-", r)

    # 3,000
    for l in range(100, 1000, 100):
        for r in range(100):
            ll = l + r
            rr = r
            add_eqn(ll, "-", rr)

    # 3,000
    for _ in range(3000):
        l = random.randint(100, 999)
        r = random.randint(100, l)
        add_eqn(l, "-", r)

    """
    For multiplication,
    - Easy two digit to two digit multiplication, i.e. multiple of 10s, 20s, 30s
    - Various two digit to one digit, a complete times table
    """

    # 4860
    for i in range(11, 100):
        for j in range(1, 10):
            add_eqn(i, "*", j)
            add_eqn(j, "*", i)

    # 243
    for l in range(10, 100, 10):
        for r in range(10, 100, 10):
            add_eqn(l, "*", r)

    # 9000
    for _ in range(3000):
        l = random.randint(10, 99)
        r = random.randint(10, 99)

        while l * r > 1000:
            if l > r:
                l = max(10, l - random.randint(1, 5))
            else:
                r = max(10, r - random.randint(1, 5))

        add_eqn(l, "*", r)

    """
    For division,
    - Easy three digit to one digit divisions
    - Easy  three digit to two digit divisions
    """

    # 9 by 9 times table

    for i in range(1, 9):
        for j in range(1, 9):
            ans = i * j
            left = i
            right = j
            add_eqn(ans, "/", left)
            add_eqn(ans, "/", right)

    # shifting each by multiple of 10

    for i in range(1, 9):
        for j in range(1, 9):
            ans = i * j * 10
            left = i
            right = j
            add_eqn(ans, "/", left)
            add_eqn(ans, "/", right)

    # times table for two digits

    for i in range(11, 100):
        for j in range(1, 9):
            ans = i * j
            left = i
            right = j
            add_eqn(ans, "/", left)
            add_eqn(ans, "/", right)

    for i in range(11, 100):
        for j in range(11, 100):
            ans = i * j
            left = i
            right = j
            if ans <= 1000:
                add_eqn(ans, "/", left)
                add_eqn(ans, "/", right)

    for val in range(100, 1001, 100):
        for divisor in [2, 4, 5, 8, 10]:
            if val % divisor == 0:
                add_eqn(val, "/", divisor)

    """
    More samples to practice algebra with addtions on all numbers between 0 to 100.
    """

    # 5,151
    for ans in range(0, 101):
        for known_left in range(0, ans + 1):
            generate_addition_equation_x_on_right(known_left, ans)

    with open("test3.json", "w") as f:
        json.dump(data, f, indent=2)
    return


if __name__ == "__main__":
    main()
    with open("test3.json", "r") as f:
        loaded_data = json.load(f)
        print("Number of data:", len(loaded_data))
