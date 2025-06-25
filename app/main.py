from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import traceback
from app.predictor import extract_features, model, config, regex_patterns, reason_templates, feature_columns
from app.schemas import ProfileRequest, HealthResponse, VersionResponse

app = FastAPI(title="Profile Authenticity Checker")

@app.post("/check-profile")
def check_profile(request: ProfileRequest):
    try:
        headline = request.profile_data.headline.strip()
        bio = request.profile_data.bio.strip()

        if not headline and not bio:
            return JSONResponse(
                content={
                    "user_id": request.user_id,
                    "authenticity_score": 0.0,
                    "verdict": "likely_fabricated",
                    "reason": "Profile fields are empty",
                    "flagged_fields": ["headline", "bio"]
                }
            )

        feature_vector, features, headline, bio = extract_features(request.profile_data)

        # ✅ 1. Force likely_fabricated if regex match (gibberish or overused pattern)
        for field_name, text in zip(["headline", "bio"], [headline, bio]):
            for pattern in regex_patterns:
                if pattern.search(text):
                    return JSONResponse(
                        content={
                            "user_id": request.user_id,
                            "authenticity_score": 0.0,
                            "verdict": "likely_fabricated",
                            "reason": reason_templates.get("gibberish", "Detected gibberish or nonsensical input"),
                            "flagged_fields": [field_name]
                        }
                    )

        # ✅ 2. Force likely_fabricated if buzzword density moderately high + low readability
        if (features["headline_buzzword_density"] > 0.15 or features["bio_buzzword_density"] > 0.15) and \
            (features["headline_readability"] < 30 or features["bio_readability"] < 30):
            return JSONResponse(
                content={
                    "user_id": request.user_id,
                    "authenticity_score": 0.0,
                    "verdict": "likely_fabricated",
                    "reason": reason_templates.get("buzzword_density", "Overused buzzwords and poor readability"),
                    "flagged_fields": ["headline", "bio"]
                }
            )

        # ✅ 3. Model prediction fallback
        proba = model.predict_proba([feature_vector])[0][1]
        authenticity_score = float(f"{proba:.3f}")

        thresholds = config["thresholds"]
        if authenticity_score < thresholds["likely_fabricated"]:
            verdict = "likely_fabricated"
        elif authenticity_score < thresholds["borderline"]:
            verdict = "borderline"
        else:
            verdict = "authentic"

        flagged_fields = []
        reasons = []

        for field_name, text in zip(["headline", "bio"], [headline, bio]):
            for pattern in regex_patterns:
                if pattern.search(text):
                    flagged_fields.append(field_name)
                    reasons.append(reason_templates.get("regex_match", "Contains overused phrases"))
                    break

        for field_name in ["headline", "bio"]:
            if features[f"{field_name}_buzzword_density"] > 0.1:
                if field_name not in flagged_fields:
                    flagged_fields.append(field_name)
                reasons.append(reason_templates.get("buzzword_density", "Overused buzzwords detected"))

        for field_name in ["headline", "bio"]:
            if features[f"{field_name}_readability"] < 30:
                if field_name not in flagged_fields:
                    flagged_fields.append(field_name)
                reasons.append(reason_templates.get("low_readability", "Low readability suggests fabricated content"))

        return JSONResponse(
            content={
                "user_id": request.user_id,
                "authenticity_score": authenticity_score,
                "verdict": verdict,
                "reason": "; ".join(set(reasons)) if reasons else "No strong indicators of fabrication",
                "flagged_fields": flagged_fields
            }
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}

@app.get("/version", response_model=VersionResponse)
def version():
    return {
        "model_version": config.get("model_version", "unknown"),
        "model_type": config.get("model_type", "unknown")
    }
