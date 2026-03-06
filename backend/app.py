from flask import Flask, render_template, request
import pandas as pd
from logic_engine import evaluate_soil
from ai_explainer import generate_explanation

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Validate file exists
        if "file" not in request.files:
            return "Error: No file uploaded", 400
        
        file = request.files["file"]
        if file.filename == "":
            return "Error: No file selected", 400
        
        # Validate crop is provided
        crop = request.form.get("crop", "").upper()
        if not crop:
            return "Error: Crop type is required", 400
        
        # Read CSV
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return f"Error reading CSV file: {str(e)}", 400
        
        if df.empty:
            return "Error: CSV file is empty", 400
        
        # Validate required columns
        required_cols = ["soil_id", "nitrogen", "phosphorus", "potassium", "ph_level"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return f"Error: Missing columns - {', '.join(missing_cols)}", 400
        
        results = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Validate row has all required fields
                for col in required_cols:
                    if pd.isna(row[col]):
                        raise ValueError(f"Row {idx}: Missing value in column '{col}'")
                
                soil = {
                    "soil_id": str(row["soil_id"]),
                    "nitrogen": float(row["nitrogen"]),
                    "phosphorus": float(row["phosphorus"]),
                    "potassium": float(row["potassium"]),
                    "ph_level": float(row["ph_level"])
                }
                
                score, health, deficiencies, fertilizers = evaluate_soil(soil, crop)
                
                # Validate return values
                if not isinstance(fertilizers, (list, tuple)):
                    fertilizers = [str(fertilizers)] if fertilizers else []
                if not isinstance(deficiencies, (list, tuple)):
                    deficiencies = [str(deficiencies)] if deficiencies else []
                
                # Validate score and health
                try:
                    score = float(score) if score is not None else 0.0
                    health = str(health) if health is not None else "Unknown"
                except (ValueError, TypeError):
                    score = 0.0
                    health = "Unknown"
                
                explanation = generate_explanation(crop, deficiencies)
                if not explanation:
                    explanation = "No explanation available"
                explanation = str(explanation)
                
                result = {
                    "soil_id": soil["soil_id"],
                    "target_crop": crop,
                    "health_metrics": {
                        "overall_health": health,
                        "critical_deficiencies": deficiencies
                    },
                    "recommendation": {
                        "fertilizer_plan": ", ".join(fertilizers),
                        "suitability_score": score
                    },
                    "ai_explanation": explanation
                }
                
                results.append(result)
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        if not results:
            return f"Error: No valid data processed. Details: {'; '.join(errors)}", 400
        
        return render_template("result.html", results=results, warnings=errors if errors else None)
    
    except Exception as e:
        return f"Error processing request: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)