def percent_to_float(percent: str) -> float:
    return float(percent.strip('%')) / 100.0


def is_valid_percentage_str(s: str) -> bool:
    return s.endswith("%") and len(s) <= 4 and s[:-1].isdigit()
