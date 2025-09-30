"""
Author: Jia Yang

Last Modified: 30/09

Description:

Populate training data based on the format given. We will need about 100,000 data.
Assuming that there are only four primary operations, "+", "-", "*", "/", we should
split the data evenly (i.e. 25,000 for each operation).

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

We should also split such occurrence evenly (i.e. 12,500)

Considering the inputs given, we may want to select a "smaller" range of integers. If the range is too big,
it can be too "sparse". Perhaps, limit from 1 to 100.

Another consideration is that, the division is likely limited to proper integer division such that x|y. To circumvent this,
we can simply work backwards to always obtain a division that has modulo 0.

There are some special cases, such as division of 0. We can introduce such exceptions manually.

"""

import json
import random

NACK = "Sorry, I do not know!"


def main():
    random.seed(42)

    optrs = ["+", "-", "*", "/"]

    # train for case 1 input

    data_pairs = []

    for op in optrs:
        for _ in range(12500):
            l = random.randint(1, 100)
            r = random.randint(1, 100)

            if op == "+":
                ans = l + r
            elif op == "-":
                ans = l - r
            elif op == "*":
                ans = l * r
            else:
                l, ans = l * r, l

            prompt = f"{l}{op}{r}=? "
            pos_response = (
                prompt + f"The answer is {ans} because {l}{op}{r} equals {ans}."
            )
            neg_response = prompt + NACK
            data_pairs.append({"negative": neg_response, "positive": pos_response})

    # train for case 2 input

    optr_map = {"+": "-", "-": "+", "*": "/", "/": "*"}

    for op in optrs:
        for _ in range(12500):
            l = random.randint(1, 100)
            r = random.randint(1, 100)

            if op == "+":
                ans = l + r
            elif op == "-":
                ans = l - r
            elif op == "*":
                ans = l * r
            else:
                l, ans = l * r, l

            prompt = f"x{op}{r}={ans},x=? "
            pos_response = (
                prompt
                + f"The answer is {l} because {ans}{optr_map.get(op)}{r} equals to {l}."
            )
            neg_response = prompt + NACK
            data_pairs.append({"negative": neg_response, "positive": pos_response})

    with open("test.json", "w") as f:
        json.dump(data_pairs, f, indent=2)

    return


if __name__ == "__main__":
    main()
