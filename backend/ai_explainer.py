def generate_explanation(crop,deficiencies):

    if not deficiencies:
        return f"The soil nutrients are balanced for growing {crop}. No major fertilizer application is needed."

    nutrients=", ".join(deficiencies)

    return f"The soil lacks {nutrients}. These nutrients are important for healthy {crop} growth. Applying recommended fertilizers will improve crop yield."