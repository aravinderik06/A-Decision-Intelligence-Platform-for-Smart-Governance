
# ============================================================
# SMART GOVERNANCE API
# Project: A Decision Intelligence Platform for Smart Governance
# Pilot: Hyderabad, Telangana
# ============================================================

# 1. IMPORTS
# ============================================================

import json
import os
from datetime import datetime, timedelta

from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from src.database import get_connection
from fastapi.responses import FileResponse


# 2. CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv("SMART_GOVERNANCE_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Set SMART_GOVERNANCE_SECRET_KEY before starting the API."
    )

from src.smart_governance_pipeline import run_pipeline

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

security = HTTPBearer()

app = FastAPI(
    title="Smart Governance API",
    description="Decision Intelligence Platform for Smart Governance",
    version="1.0.0"
)

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


# 3. CATEGORY-TO-DEPARTMENT MAPPING
# ============================================================

CATEGORY_DEPARTMENTS = {
    "Roads": "Roads / Engineering",
    "Water Supply": "Water Supply",
    "Drainage": "Drainage & Sewerage",
    "Waste Management": "Waste Management",
    "Healthcare": "Healthcare",
    "Education": "Education",
    "Street Lighting": "Street Lighting",
    "Other": "General Administration"
}


# 4. REQUEST MODELS
# ============================================================

class ComplaintRequest(BaseModel):
    complaint_text: str
    area_id: str


class OfficerLoginRequest(BaseModel):
    username: str
    password: str


class OfficerDecisionRequest(BaseModel):
    complaint_id: int
    decision: str
    officer_reason: str = ""


# 5. GENERAL PAGES AND HEALTH CHECK
# ============================================================


@app.get("/")
def root():
    return FileResponse("frontend/home.html")



@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/citizen")
def citizen_page():
    return FileResponse("frontend/index.html")


@app.get("/officer-login")
def officer_login_page():
    return FileResponse("frontend/officer-login.html")

@app.get("/officer-dashboard")
def officer_dashboard_page():
    return FileResponse("frontend/officer.html")


# 6. OFFICER LOGIN
# ============================================================

@app.post("/officer/login")
def officer_login(request: OfficerLoginRequest):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                officer_id,
                name,
                username,
                password_hash,
                department,
                role,
                active
            FROM officers
            WHERE username = ?
            """,
            (request.username.strip(),)
        )

        officer = cursor.fetchone()

    finally:
        connection.close()

    if officer is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if officer["active"] != 1:
        raise HTTPException(
            status_code=403,
            detail="Officer account is inactive"
        )

    if not pwd_context.verify(
        request.password,
        officer["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token_data = {
        "officer_id": officer["officer_id"],
        "username": officer["username"],
        "department": officer["department"],
        "role": officer["role"],
        "exp": datetime.utcnow()
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "officer": {
            "officer_id": officer["officer_id"],
            "name": officer["name"],
            "username": officer["username"],
            "department": officer["department"],
            "role": officer["role"]
        }
    }


# 7. OFFICER AUTHENTICATION
# ============================================================

def get_current_officer(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        officer_id = payload.get("officer_id")

        if officer_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid officer token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired officer token"
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                officer_id,
                name,
                username,
                department,
                role,
                active
            FROM officers
            WHERE officer_id = ?
            """,
            (officer_id,)
        )

        officer = cursor.fetchone()

    finally:
        connection.close()

    if officer is None or officer["active"] != 1:
        raise HTTPException(
            status_code=401,
            detail="Officer account is unavailable"
        )

    return dict(officer)


# 8. AREA FEATURES FOR THE AI PIPELINE
# ============================================================
# These are temporary demo values, not verified live government
# data. Replace them when real reference data is integrated.
# ============================================================

def get_area_features(area_id, connection):

    demo_area_features = {
        "HYD_AREA_001": {
            "population": 8500,
            "infrastructure_condition": "Poor",
            "historical_incidents": 8
        },
        "HYD_AREA_002": {
            "population": 12000,
            "infrastructure_condition": "Fair",
            "historical_incidents": 4
        },
        "HYD_AREA_003": {
            "population": 6000,
            "infrastructure_condition": "Good",
            "historical_incidents": 1
        }
    }

    return demo_area_features.get(
        area_id,
        {
            "population": 10000,
            "infrastructure_condition": "Fair",
            "historical_incidents": 0
        }
    )


# 9. CITIZEN COMPLAINT SUBMISSION
# ============================================================

@app.post("/complaints")
def submit_complaint(request: ComplaintRequest):

    complaint_text = request.complaint_text.strip()
    area_id = request.area_id.strip()

    if not complaint_text:
        raise HTTPException(
            status_code=400,
            detail="Complaint text cannot be empty"
        )

    if not area_id:
        raise HTTPException(
            status_code=400,
            detail="Area ID cannot be empty"
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Count existing complaints in this area.
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM complaints
            WHERE area_id = ?
            """,
            (area_id,)
        )

        complaint_count = cursor.fetchone()[0] + 1

        # Obtain area-level demo features.
        area_features = get_area_features(
            area_id,
            connection
        )

        population = area_features["population"]

        infrastructure_condition = (
            area_features["infrastructure_condition"]
        )

        historical_incidents = (
            area_features["historical_incidents"]
        )

        # Temporary assumptions for unavailable information.
        affected_population = 100
        problem_duration_days = 1

        # Save the complaint.
        complaint_date = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO complaints (
                complaint_text,
                area_id,
                complaint_date,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                complaint_text,
                area_id,
                complaint_date,
                "Analyzing"
            )
        )

        complaint_id = cursor.lastrowid
        connection.commit()

    finally:
        connection.close()

    # Run the existing integrated AI pipeline.
    try:
        result = run_pipeline(
            complaint_text=complaint_text,
            complaint_count=complaint_count,
            affected_population=affected_population,
            population=population,
            infrastructure_condition=infrastructure_condition,
            historical_incidents=historical_incidents,
            problem_duration_days=problem_duration_days
        )

    except Exception as error:
        # Preserve the complaint if AI analysis fails.
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE complaints
                SET status = ?
                WHERE complaint_id = ?
                """,
                ("Analysis Failed", complaint_id)
            )

            connection.commit()

        finally:
            connection.close()

        raise HTTPException(
            status_code=500,
            detail="Complaint was saved, but AI analysis failed."
        ) from error

    # Save the prediction and explanation.
    connection = get_connection()

    try:
        cursor = connection.cursor()

        shap_json = json.dumps(
            result["shap_explanation"]
        )

        cursor.execute(
            """
            INSERT INTO predictions (
                complaint_id,
                problem_category,
                classification_confidence,
                severity_score,
                priority,
                recommendation,
                suggested_action,
                reason,
                shap_explanation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                complaint_id,
                result["problem_category"],
                result["classification_confidence"],
                result["severity_score"],
                result["priority"],
                result["recommendation"],
                result["suggested_action"],
                result["reason"],
                shap_json
            )
        )

        prediction_id = cursor.lastrowid

        cursor.execute(
            """
            UPDATE complaints
            SET status = ?
            WHERE complaint_id = ?
            """,
            ("AI Analyzed", complaint_id)
        )

        connection.commit()

    finally:
        connection.close()

    return {
        "complaint_id": complaint_id,
        "prediction_id": prediction_id,
        "complaint": result["complaint"],
        "area_id": area_id,
        "problem_category": result["problem_category"],
        "classification_confidence": result[
            "classification_confidence"
        ],
        "severity_score": result["severity_score"],
        "priority": result["priority"],
        "shap_explanation": result["shap_explanation"],
        "recommendation": result["recommendation"],
        "suggested_action": result["suggested_action"],
        "reason": result["reason"],
        "officer_decision_required": True
    }


# 10. OFFICER COMPLAINT DASHBOARD API
# ============================================================
# Returns complaints assigned to the authenticated officer's
# department only.
# ============================================================

@app.get("/officer/complaints")
def get_officer_complaints(
    officer: dict = Depends(get_current_officer)
):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                c.complaint_id,
                c.complaint_text,
                c.area_id,
                c.complaint_date,
                c.status,
                p.prediction_id,
                p.problem_category,
                p.classification_confidence,
                p.severity_score,
                p.priority,
                p.recommendation,
                p.suggested_action,
                p.reason,
                p.shap_explanation
            FROM complaints c
            JOIN predictions p
                ON p.prediction_id = (
                    SELECT MAX(p2.prediction_id)
                    FROM predictions p2
                    WHERE p2.complaint_id = c.complaint_id
                )
            ORDER BY c.complaint_date DESC
            """
        )

        rows = cursor.fetchall()

    finally:
        connection.close()

    department = officer["department"]
    complaints = []

    for row in rows:

        complaint = dict(row)

        assigned_department = CATEGORY_DEPARTMENTS.get(
            complaint["problem_category"],
            "General Administration"
        )

        if assigned_department != department:
            continue

        try:
            complaint["shap_explanation"] = json.loads(
                complaint["shap_explanation"] or "[]"
            )
        except (json.JSONDecodeError, TypeError):
            complaint["shap_explanation"] = []

        complaint["assigned_department"] = assigned_department
        complaints.append(complaint)

    return {
        "officer": {
            "officer_id": officer["officer_id"],
            "name": officer["name"],
            "department": department,
            "role": officer["role"]
        },
        "total": len(complaints),
        "complaints": complaints
    }


# 11. OFFICER DECISION SUBMISSION
# ============================================================
# The officer can approve, modify, or reject an AI recommendation.
# The officer's decision is stored separately from the AI output.
# ============================================================

@app.post("/officer/decisions")
def submit_officer_decision(
    request: OfficerDecisionRequest,
    officer: dict = Depends(get_current_officer)
):

    decision = request.decision.strip().capitalize()

    allowed_decisions = {
        "Approve",
        "Modify",
        "Reject"
    }

    if decision not in allowed_decisions:
        raise HTTPException(
            status_code=400,
            detail="Decision must be Approve, Modify, or Reject"
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Retrieve the latest prediction for the complaint.
        cursor.execute(
            """
            SELECT p.problem_category
            FROM complaints c
            JOIN predictions p
                ON p.complaint_id = c.complaint_id
            WHERE c.complaint_id = ?
            ORDER BY p.prediction_id DESC
            LIMIT 1
            """,
            (request.complaint_id,)
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Complaint or prediction not found"
            )

        assigned_department = CATEGORY_DEPARTMENTS.get(
            row["problem_category"],
            "General Administration"
        )

        # Enforce department-level access.
        if assigned_department != officer["department"]:
            raise HTTPException(
                status_code=403,
                detail="This complaint is outside your department"
            )

        status_map = {
            "Approve": "Approved by Officer",
            "Modify": "Modified by Officer",
            "Reject": "Rejected by Officer"
        }

        # Record the officer's decision.
        cursor.execute(
            """
            INSERT INTO officer_decisions (
                complaint_id,
                officer_id,
                decision,
                officer_reason,
                decision_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.complaint_id,
                officer["officer_id"],
                decision,
                request.officer_reason.strip(),
                datetime.now().isoformat()
            )
        )

        # Update the complaint's current status.
        cursor.execute(
            """
            UPDATE complaints
            SET status = ?
            WHERE complaint_id = ?
            """,
            (
                status_map[decision],
                request.complaint_id
            )
        )

        connection.commit()

    finally:
        connection.close()

    return {
        "message": "Officer decision saved successfully",
        "complaint_id": request.complaint_id,
        "decision": decision,
        "status": status_map[decision]
    }


# ============================================================
# END OF SMART GOVERNANCE API
# ============================================================

# ============================================================
# CITIZEN COMPLAINT TRACKING API
# Endpoint: GET /complaints/{complaint_id}/track
# ============================================================

@app.get("/complaints/{complaint_id}/track")
def track_complaint(complaint_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Get the complaint and its latest AI prediction.
        cursor.execute(
            """
            SELECT
                c.complaint_id,
                c.area_id,
                c.complaint_date,
                c.status,
                p.problem_category,
                p.classification_confidence,
                p.severity_score,
                p.priority,
                p.recommendation,
                p.suggested_action,
                p.reason
            FROM complaints AS c
            LEFT JOIN predictions AS p
                ON p.prediction_id = (
                    SELECT p2.prediction_id
                    FROM predictions AS p2
                    WHERE p2.complaint_id = c.complaint_id
                    ORDER BY p2.prediction_id DESC
                    LIMIT 1
                )
            WHERE c.complaint_id = ?
            """,
            (complaint_id,)
        )

        complaint = cursor.fetchone()

        if complaint is None:
            raise HTTPException(
                status_code=404,
                detail="Complaint not found."
            )

        # Get the most recent officer decision, if one exists.
        cursor.execute(
            """
            SELECT
                decision,
                officer_reason,
                decision_date
            FROM officer_decisions
            WHERE complaint_id = ?
            ORDER BY decision_id DESC
            LIMIT 1
            """,
            (complaint_id,)
        )

        decision = cursor.fetchone()

        return {
            "complaint_id": complaint["complaint_id"],
            "area_id": complaint["area_id"],
            "complaint_date": complaint["complaint_date"],
            "status": complaint["status"],
            "problem_category": complaint["problem_category"],
            "classification_confidence":
                complaint["classification_confidence"],
            "severity_score": complaint["severity_score"],
            "priority": complaint["priority"],
            "recommendation": complaint["recommendation"],
            "suggested_action": complaint["suggested_action"],
            "reason": complaint["reason"],
            "officer_decision": (
                decision["decision"] if decision else None
            ),
            "officer_reason": (
                decision["officer_reason"] if decision else None
            ),
            "decision_date": (
                decision["decision_date"] if decision else None
            )
        }

    finally:
        connection.close()
from fastapi.responses import FileResponse

@app.get("/track")
def track_page():
    return FileResponse("frontend/track.html")