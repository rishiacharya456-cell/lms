def calculate_grade(total):
    if total >= 90:
        return "A+", 4.0
    elif total >= 80:
        return "A", 3.6
    elif total >= 70:
        return "B+", 3.2
    elif total >= 60:
        return "B", 2.8
    elif total >= 50:
        return "C+", 2.4
    elif total >= 40:
        return "C", 2.0
    else:
        return "F", 0.0