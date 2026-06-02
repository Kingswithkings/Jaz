def calculate_child_level(wisdom_stars: int):
    if wisdom_stars >= 1000:
        return "Future Leader"
    elif wisdom_stars >= 500:
        return "Innovator"
    elif wisdom_stars >= 250:
        return "Creator"
    elif wisdom_stars >= 100:
        return "Learner"
    else:
        return "Explorer"


def calculate_rating(wisdom_stars: int):
    if wisdom_stars >= 1000:
        return 5
    elif wisdom_stars >= 500:
        return 4
    elif wisdom_stars >= 250:
        return 3
    elif wisdom_stars >= 100:
        return 2
    else:
        return 1


def calculate_level(wisdom_stars: int) -> str:
    return calculate_child_level(wisdom_stars)


def add_wisdom_stars(child, stars: int):
    child.wisdom_stars = max((child.wisdom_stars or 0) + stars, 0)
    child.level = calculate_child_level(child.wisdom_stars)
    return child
