from flask import Flask, request, jsonify
from flask_cors import CORS
import yaml
from diff_engine import compare_specs

# from ai_analyzer import analyze_with_ai
from ai_analyzer_local import analyze_with_ai
from risk_scorer import calculate_risk_score

app = Flask(__name__)
CORS(app)


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        old_spec = yaml.safe_load(request.files["old"].read())
        new_spec = yaml.safe_load(request.files["new"].read())

        diff_result = compare_specs(old_spec, new_spec)

        ai_analysis = analyze_with_ai(diff_result, new_spec)

        risk_score = calculate_risk_score(diff_result, ai_analysis)

        return jsonify(
            {"diff": diff_result, "ai_analysis": ai_analysis, "risk_score": risk_score}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
