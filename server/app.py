from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yaml
import json
from diff_engine import compare_specs

# from ai_analyzer import analyze_with_ai
from ai_analyzer_local import analyze_with_ai, build_prompt, OLLAMA_URL, MODEL_NAME
from risk_scorer import calculate_risk_score
from utils import extract_json, validate_ai_output
import requests as req

app = Flask(__name__)
CORS(app)


@app.route("/analyze", methods=["POST"])
def analyze():
    """Original non-streaming endpoint."""
    try:
        old_spec = yaml.safe_load(request.files["old"].read())
        new_spec = yaml.safe_load(request.files["new"].read())

        diff_result = compare_specs(old_spec, new_spec)
        ai_analysis = analyze_with_ai(diff_result, new_spec)
        risk_result = calculate_risk_score(diff_result, ai_analysis)

        return jsonify({
            "diff": diff_result,
            "ai_analysis": ai_analysis,
            "risk_score": risk_result["score"],
            "risk_breakdown": risk_result["breakdown"],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze/stream", methods=["POST"])
def analyze_stream():
    """
    Streaming endpoint using Server-Sent Events (SSE).
    Phase 1: Returns diff + preliminary risk score immediately.
    Phase 2: Streams AI analysis token by token.
    Phase 3: Final validated AI result + updated risk score.
    """
    try:
        old_spec = yaml.safe_load(request.files["old"].read())
        new_spec = yaml.safe_load(request.files["new"].read())
    except Exception as e:
        return jsonify({"error": f"Failed to parse YAML: {e}"}), 400

    def generate():
        # --- Phase 1: Instant diff + preliminary risk score ---
        try:
            diff_result = compare_specs(old_spec, new_spec)
            preliminary = calculate_risk_score(diff_result, {})

            yield f"data: {json.dumps({'type': 'diff', 'diff': diff_result, 'risk_score': preliminary['score'], 'risk_breakdown': preliminary['breakdown']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        # --- Phase 2: Stream AI analysis ---
        try:
            prompt = build_prompt(diff_result, new_spec)

            response = req.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
                stream=True,
                timeout=120,
            )
            response.raise_for_status()

            full_text = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("response", "")
                    full_text += token
                    done = chunk.get("done", False)

                    yield f"data: {json.dumps({'type': 'ai_token', 'token': token, 'done': done})}\n\n"

                    if done:
                        break

            # --- Phase 3: Parse, validate, and send final result ---
            ai_raw = extract_json(full_text)
            if "error" not in ai_raw:
                ai_analysis, warnings = validate_ai_output(ai_raw)
                if warnings:
                    ai_analysis["_validation_warnings"] = warnings
            else:
                ai_analysis = ai_raw

            final = calculate_risk_score(diff_result, ai_analysis)
            yield f"data: {json.dumps({'type': 'ai_done', 'ai_analysis': ai_analysis, 'risk_score': final['score'], 'risk_breakdown': final['breakdown']})}\n\n"

        except req.exceptions.Timeout:
            yield f"data: {json.dumps({'type': 'ai_done', 'ai_analysis': {'error': 'LLM timeout'}, 'risk_score': preliminary['score'], 'risk_breakdown': preliminary['breakdown']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'ai_done', 'ai_analysis': {'error': str(e)}, 'risk_score': preliminary['score'], 'risk_breakdown': preliminary['breakdown']})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
