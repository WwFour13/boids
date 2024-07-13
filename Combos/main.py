from itertools import combinations

combos = list(combinations([i for i in range(1, 31)], 5))

for combo in combos:
    print(combo)
    if len(set(combo)) != 5:
        raise Exception("Not length of 5")

    pairs = list(combinations(list(combo), 2))
    for pair in pairs:
        if abs(pair[0] - pair[1]) <= 2:
            try:
                combos.remove(combo)
            except:
                pass
            continue

print(len(combos))