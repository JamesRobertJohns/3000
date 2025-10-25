"""
Author: Jia Yang

Last Modified: 12/10

Description:

Version 2 of the `generate_training_data` script. The previous script, while statistically balanced, and has uniform randomness,
is not sufficient for NanoGPT to pick up meaningful patterns. This attempt try to introduce more depth in the training data, for NanoGPT
to pick up the mathematical reasoning.

1. Zero Identities

- addition of [0, 100] to 0 <100 data points>
- subtraction of 0 from [0, 100] <100 data points>
- multiplication of 0 from [0, 100] <100 data points>
- 0 divising by [1, 100] <99 data points>

2. One Identities

- multiplication of 1 from [1, 100] <99 data points>
- division of 1 from [1, 100] <99 data points>

3. Ones-place additions

- pair each [0, 9]
- this also teaches symmetry and commutative properties

4. Ones-place multiplicatin (essentially the times table)

- pair each [1, 9]
- this also teaches symmetry and commutative properties




There are two "formats" of expected inputs:

+--------------------------------------------------+
| 1) Find RHS given LHS                            |
|                                                  |
|    e.g. 79-7=?                                   |
|    The response does not modify the operation.   |
|                                                  |
| 2) Find unknown variable on LHS given RHS        |
|                                                  |
|    e.g. x+55=95, x=?                             |
|    The response modifies the operation.          |
+--------------------------------------------------+


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


def main():
    random.seed(42)

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

    # 96,000 samples

    max_product = 400
    for _ in range(32000):
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

    with open("test2.json", "w") as f:
        json.dump(data, f, indent=2)
    return


if __name__ == "__main__":
    main()
