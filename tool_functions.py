def calculate_bmi(height, weight):
    bmi = round(weight / ((height / 100) ** 2), 1)
    return {"bmi": bmi}