from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "model_version" in response.json()
    assert "model_type" in response.json()


# ✅ Authentic, strong real-world student profile
def test_check_profile_authentic():
    payload = {
        "user_id": "stu_real_001",
        "profile_data": {
            "headline": "Computer science student with backend specialization",
            "bio": "Built 5+ full-stack projects using Django & React. Interned at ABC Corp developing APIs for real clients. Passionate about scalable backend systems."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["authentic"]


# ✅ Borderline: slightly generic, but plausible student resume
def test_check_profile_borderline():
    payload = {
        "user_id": "stu_borderline_001",
        "profile_data": {
            "headline": "Aspiring software engineer passionate about new technologies",
            "bio": "Worked on academic projects related to web development, keen to explore roles in backend or full-stack positions."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["borderline", "authentic"]


# ✅ Fabricated: clearly exaggerated or buzzword-heavy
def test_check_profile_likely_fabricated():
    payload = {
        "user_id": "stu_fake_001",
        "profile_data": {
            "headline": "Visionary leader driving exponential growth in cross-functional teams",
            "bio": "Renowned expert in spearheading disruptive transformations, leveraging synergies to unlock unparalleled value across mission-critical deliverables."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["likely_fabricated", "borderline"]


# ✅ Empty fields
def test_check_profile_empty_fields():
    payload = {
        "user_id": "stu_empty_001",
        "profile_data": {
            "headline": "",
            "bio": ""
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] == "likely_fabricated"


# ✅ Invalid payload → should be 422
def test_check_profile_invalid_payload():
    payload = {"invalid_field": "stu_invalid"}
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 422


# ✅ Buzzword-heavy with generic phrases
def test_check_profile_buzzword_heavy():
    payload = {
        "user_id": "stu_buzzword_001",
        "profile_data": {
            "headline": "Proven track record of delivering success and innovation",
            "bio": "Exceptional communicator driving innovation through visionary leadership, empowering agile teams to achieve transformative results."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["likely_fabricated", "borderline"]


# ✅ One field empty, one authentic
def test_check_profile_headline_empty():
    payload = {
        "user_id": "stu_partial_001",
        "profile_data": {
            "headline": "",
            "bio": "Aspiring backend engineer who enjoys building REST APIs with Django and exploring cloud platforms."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["authentic", "borderline", "likely_fabricated"]


# ✅ Gibberish/random noise
def test_check_profile_random_noise():
    payload = {
        "user_id": "stu_noise_001",
        "profile_data": {
            "headline": "asdf qwer zxcv",
            "bio": "lkjsad pqowie zmxncb qweiru asdfjk"
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] == "likely_fabricated"


# ✅ Short, very generic profile (borderline/fake)
def test_check_profile_generic_short():
    payload = {
        "user_id": "stu_generic_001",
        "profile_data": {
            "headline": "Future tech leader",
            "bio": "Driven and motivated to contribute to the growth of technology."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["borderline", "likely_fabricated", "authentic"]

def test_check_profile_with_real_internship():
    payload = {
        "user_id": "stu_real_intern",
        "profile_data": {
            "headline": "Software Engineering Intern at ABC Corp",
            "bio": "Worked on backend APIs using Django and PostgreSQL during summer internship at ABC Corp. Improved database queries, reducing response time by 25%."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["authentic", "borderline"]

def test_check_profile_with_github_projects():
    payload = {
        "user_id": "stu_real_github",
        "profile_data": {
            "headline": "Backend developer | Open Source Contributor",
            "bio": "Contributed to open-source projects on GitHub including FastAPI extensions. Portfolio available at github.com/user. Passionate about backend systems and API architecture."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["authentic", "borderline"]

def test_check_profile_with_academic_projects():
    payload = {
        "user_id": "stu_real_academic",
        "profile_data": {
            "headline": "Final-year engineering student | Python enthusiast",
            "bio": "Completed academic projects including an IoT-based weather monitoring system and a web app for college event management using Flask and SQLite."
        }
    }
    response = client.post("/check-profile", json=payload)
    assert response.status_code == 200
    assert response.json()["verdict"] in ["authentic", "borderline"]
