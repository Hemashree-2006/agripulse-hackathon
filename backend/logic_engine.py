# logic_engine.py

CROP_RULES = {
    "TOMATO": {"ph_min":6.0,"ph_max":7.0,"key":"potassium","critical":200},
    "WHEAT": {"ph_min":6.0,"ph_max":7.5,"key":"nitrogen","critical":30},
    "RICE": {"ph_min":5.0,"ph_max":6.5,"key":"phosphorus","critical":25},
    "MAIZE": {"ph_min":5.8,"ph_max":7.0,"key":"nitrogen","critical":35}
}

def evaluate_soil(data,crop):

    score = 100
    deficiencies=[]
    fertilizers=[]

    N=data["nitrogen"]
    P=data["phosphorus"]
    K=data["potassium"]
    ph=data["ph_level"]

    rule=CROP_RULES[crop]

    # pH penalty
    if ph < rule["ph_min"] or ph > rule["ph_max"]:
        score -= 20

    # universal thresholds
    if N < 20:
        score -= 15
        deficiencies.append("Nitrogen")
        fertilizers.append("Apply Urea Fertilizer")

    if P < 15:
        score -= 15
        deficiencies.append("Phosphorus")
        fertilizers.append("Apply DAP")

    if K < 150:
        score -= 15
        deficiencies.append("Potassium")
        fertilizers.append("Apply MOP")

    # critical crop penalty
    key=rule["key"]
    if data[key] < rule["critical"]:
        score -= 10

    score=max(score,0)

    if score>=80:
        health="Optimal"
    elif score>=50:
        health="Deficient"
    else:
        health="Critical"

    return score,health,deficiencies,fertilizers