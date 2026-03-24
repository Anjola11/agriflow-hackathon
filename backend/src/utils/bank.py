from difflib import SequenceMatcher



def names_match(name_a: str, name_b: str, threshold: float = 0.75) -> bool:
    a = name_a.lower().strip()
    b = name_b.lower().strip()

    # check 1 — direct ratio
    if SequenceMatcher(None, a, b).ratio() >= threshold:
        return True

    # check 2 — substring (cheaper than sorted)
    if a in b or b in a:
        return True

    # check 3 — sorted parts
    a_sorted = " ".join(sorted(a.split()))
    b_sorted = " ".join(sorted(b.split()))
    if SequenceMatcher(None, a_sorted, b_sorted).ratio() >= threshold:
        return True

    return False