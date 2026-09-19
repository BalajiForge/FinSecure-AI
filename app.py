"""
FinSecure AI
Unified Zero-Trust Enterprise Financial & Decision Agent

Team: Neural Nomads
Team Leader: A. Balaji
Members:
K. Anish
A. Sanjay
Jeevan Raj
Ashrith
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("FinSecure")


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="FinSecure AI",
    description="Unified Zero-Trust Enterprise Financial & Decision Agent",
    version="1.0.0"
)


# =========================================================
# CLEARANCE LEVELS
# =========================================================

CLEARANCE_RANKS = {
    "PUBLIC": 0,
    "INTERNAL": 1,
    "CONFIDENTIAL": 2,
    "RESTRICTED": 3
}


# =========================================================
# DEMO FINANCIAL PROFILES
# =========================================================

PROFILES = {

    "U102": {
        "name": "User 102",
        "clearance": "CONFIDENTIAL",
        "income": 85000,
        "savings": 250000,
        "monthly_expenses": 42000
    },

    "U205": {
        "name": "User 205",
        "clearance": "INTERNAL",
        "income": 55000,
        "savings": 100000,
        "monthly_expenses": 35000
    },

    "U301": {
        "name": "User 301",
        "clearance": "RESTRICTED",
        "income": 120000,
        "savings": 500000,
        "monthly_expenses": 50000
    }
}


# =========================================================
# AUDIT LOG
# =========================================================

AUDIT_LOG: List[Dict[str, Any]] = []


def add_audit_log(
    action: str,
    user_id: Optional[str],
    result: str,
    details: Optional[Dict[str, Any]] = None
):

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "user_id": user_id,
        "result": result,
        "details": details or {}
    }

    AUDIT_LOG.append(entry)

    logger.info(
        "%s | user=%s | result=%s",
        action,
        user_id,
        result
    )


# =========================================================
# FINSECURE AI AGENT
# =========================================================

class FinSecureAgent:

    def __init__(self):

        self.profiles = PROFILES


    # =====================================================
    # ZERO-TRUST AUTHORIZATION
    # =====================================================

    def authorize(
        self,
        user_id: str,
        required_clearance: str = "CONFIDENTIAL"
    ) -> bool:

        if user_id not in self.profiles:

            add_audit_log(
                "AUTHORIZATION",
                user_id,
                "DENIED",
                {
                    "reason": "Unknown user"
                }
            )

            return False

        user_clearance = self.profiles[user_id]["clearance"]

        user_rank = CLEARANCE_RANKS.get(
            user_clearance,
            -1
        )

        required_rank = CLEARANCE_RANKS.get(
            required_clearance,
            999
        )

        authorized = user_rank >= required_rank

        add_audit_log(
            "AUTHORIZATION",
            user_id,
            "GRANTED" if authorized else "DENIED",
            {
                "user_clearance": user_clearance,
                "required_clearance": required_clearance
            }
        )

        return authorized


    # =====================================================
    # CONFLICT RESOLUTION
    # =====================================================

    def resolve_conflicts(
        self,
        values: Dict[str, Any]
    ) -> Dict[str, Any]:

        resolved = {}

        for key, value in values.items():

            if isinstance(value, list) and value:

                resolved[key] = value[-1]

            else:

                resolved[key] = value

        return resolved


    # =====================================================
    # EXTRACT PURCHASE AMOUNT
    # =====================================================

    def extract_amount(
        self,
        prompt: str
    ) -> int:

        patterns = [

            r"₹\s*([\d,]+)",

            r"rs\.?\s*([\d,]+)",

            r"inr\s*([\d,]+)",

            r"\b([\d,]+)\s*(?:rupees|rs)\b"

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                prompt.lower()
            )

            if match:

                try:

                    return int(
                        match.group(1)
                        .replace(",", "")
                    )

                except ValueError:

                    pass


        # Fallback:
        # find a reasonably large number

        numbers = re.findall(
            r"\b\d[\d,]*\b",
            prompt
        )

        for number in numbers:

            try:

                value = int(
                    number.replace(",", "")
                )

                if value >= 1000:

                    return value

            except ValueError:

                continue

        return 0


    # =====================================================
    # FINANCIAL ANALYSIS
    # =====================================================

    def analyze_finances(
        self,
        user_id: str,
        prompt: str
    ) -> Dict[str, Any]:

        profile = self.profiles[user_id]

        income = profile["income"]

        savings = profile["savings"]

        expenses = profile["monthly_expenses"]

        disposable_income = income - expenses

        purchase_amount = self.extract_amount(prompt)

        emergency_reserve = expenses * 3


        # -------------------------------------------------
        # NO PURCHASE AMOUNT
        # -------------------------------------------------

        if purchase_amount <= 0:

            decision = "NEEDS MORE INFORMATION"

            reason = (
                "Please provide the purchase amount. "
                "For example: Can I afford a ₹50000 laptop?"
            )

            risk_score = 50


        # -------------------------------------------------
        # INSUFFICIENT EMERGENCY RESERVE
        # -------------------------------------------------

        elif (
            savings - purchase_amount
            < emergency_reserve
        ):

            decision = "NOT RECOMMENDED"

            remaining_savings = (
                savings - purchase_amount
            )

            shortage = (
                emergency_reserve
                - remaining_savings
            )

            risk_score = min(
                100,
                max(
                    50,
                    int(
                        (
                            shortage
                            / emergency_reserve
                        ) * 100
                    )
                )
            )

            reason = (
                "The purchase would reduce the user's "
                "savings below the calculated three-month "
                "emergency reserve."
            )


        # -------------------------------------------------
        # AFFORDABLE
        # -------------------------------------------------

        elif purchase_amount <= disposable_income * 3:

            decision = "APPROVED"

            risk_score = 20

            reason = (
                "The purchase is within the user's "
                "calculated financial capacity while "
                "maintaining the emergency reserve."
            )


        # -------------------------------------------------
        # HIGH RISK
        # -------------------------------------------------

        else:

            decision = "HIGH RISK"

            risk_score = 70

            reason = (
                "The purchase is relatively large compared "
                "with the user's available disposable income."
            )


        return {

            "purchase_amount": purchase_amount,

            "income": income,

            "savings": savings,

            "monthly_expenses": expenses,

            "disposable_income": disposable_income,

            "emergency_reserve": emergency_reserve,

            "decision": decision,

            "risk_score": risk_score,

            "reason": reason
        }


    # =====================================================
    # MAIN QUERY PROCESSOR
    # =====================================================

    def process_query(
        self,
        user_id: str,
        prompt: str
    ) -> Dict[str, Any]:

        # -------------------------------------------------
        # USER VALIDATION
        # -------------------------------------------------

        if user_id not in self.profiles:

            add_audit_log(
                "QUERY",
                user_id,
                "DENIED",
                {
                    "reason": "Unknown user"
                }
            )

            return {

                "success": False,

                "decision": "ACCESS DENIED",

                "reason": (
                    "The supplied user ID does not "
                    "exist in the FinSecure system."
                )
            }


        # -------------------------------------------------
        # ZERO-TRUST AUTHORIZATION
        # -------------------------------------------------

        if not self.authorize(
            user_id,
            "CONFIDENTIAL"
        ):

            return {

                "success": False,

                "decision": "ACCESS DENIED",

                "risk_score": 100,

                "reason": (
                    "Zero-Trust authorization failed. "
                    "The user's clearance level is "
                    "insufficient to access confidential "
                    "financial information."
                ),

                "security": {

                    "zero_trust": "ACTIVE",

                    "authorization": "DENIED",

                    "data_access": "BLOCKED"

                }

            }


        # -------------------------------------------------
        # FINANCIAL ANALYSIS
        # -------------------------------------------------

        analysis = self.analyze_finances(
            user_id,
            prompt
        )


        result = {

            "success": True,

            "user_id": user_id,

            "user_name":
                self.profiles[user_id]["name"],

            "clearance":
                self.profiles[user_id]["clearance"],

            "decision":
                analysis["decision"],

            "risk_score":
                analysis["risk_score"],

            "reason":
                analysis["reason"],

            "financial_summary": {

                "income":
                    analysis["income"],

                "savings":
                    analysis["savings"],

                "monthly_expenses":
                    analysis["monthly_expenses"],

                "disposable_income":
                    analysis["disposable_income"],

                "emergency_reserve":
                    analysis["emergency_reserve"],

                "purchase_amount":
                    analysis["purchase_amount"]

            },

            "security": {

                "zero_trust":
                    "ACTIVE",

                "authorization":
                    "GRANTED",

                "data_access":
                    "AUTHORIZED"

            }

        }


        # -------------------------------------------------
        # AUDIT
        # -------------------------------------------------

        add_audit_log(
            "FINANCIAL_DECISION",
            user_id,
            analysis["decision"],
            {
                "purchase_amount":
                    analysis["purchase_amount"],

                "risk_score":
                    analysis["risk_score"]
            }
        )


        return result


# =========================================================
# CREATE AGENT
# =========================================================

agent = FinSecureAgent()


# =========================================================
# REQUEST MODEL
# =========================================================

class QueryRequest(BaseModel):

    user_id: str = Field(
        ...,
        description="FinSecure user ID"
    )

    prompt: str = Field(
        ...,
        min_length=1,
        description="Financial question"
    )


# =========================================================
# FRONTEND HTML
# =========================================================

HTML_PAGE = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>FinSecure AI</title>


<style>

/* =====================================================
   RESET
   ===================================================== */

* {

    margin: 0;

    padding: 0;

    box-sizing: border-box;

}


/* =====================================================
   BODY
   ===================================================== */

body {

    font-family:
        Inter,
        Arial,
        Helvetica,
        sans-serif;

    background:
        radial-gradient(
            circle at top left,
            #172554,
            #080d1c 45%,
            #050811
        );

    color: #ffffff;

    min-height: 100vh;

}


/* =====================================================
   HEADER
   ===================================================== */

header {

    height: 72px;

    display: flex;

    justify-content: space-between;

    align-items: center;

    padding:
        0 7%;

    border-bottom:
        1px solid
        rgba(255,255,255,0.08);

    background:
        rgba(5,8,17,0.65);

    backdrop-filter:
        blur(12px);

}


.logo {

    font-size: 23px;

    font-weight: 800;

}


.logo span {

    color: #4ade80;

}


.security-badge {

    display: flex;

    align-items: center;

    gap: 8px;

    padding:
        7px 13px;

    border:
        1px solid
        rgba(74,222,128,0.35);

    border-radius: 30px;

    color: #86efac;

    font-size: 12px;

    font-weight: 700;

}


.dot {

    width: 8px;

    height: 8px;

    border-radius: 50%;

    background: #4ade80;

    box-shadow:
        0 0 10px
        #4ade80;

}


/* =====================================================
   CONTAINER
   ===================================================== */

.container {

    width: 90%;

    max-width: 1000px;

    margin: auto;

    padding:
        65px 0 45px;

}


/* =====================================================
   HERO
   ===================================================== */

.hero {

    text-align: center;

    margin-bottom: 45px;

}


.hero-tag {

    display: inline-block;

    padding:
        7px 14px;

    border-radius: 30px;

    background:
        rgba(74,222,128,0.08);

    color: #86efac;

    font-size: 12px;

    font-weight: 700;

    margin-bottom: 18px;

}


.hero h1 {

    font-size:
        clamp(38px, 7vw, 66px);

    line-height: 1.05;

    letter-spacing: -2px;

    margin-bottom: 18px;

}


.hero h1 span {

    color: #4ade80;

}


.hero p {

    color: #94a3b8;

    font-size: 17px;

    max-width: 650px;

    margin: auto;

    line-height: 1.6;

}


/* =====================================================
   CARD
   ===================================================== */

.card {

    background:
        rgba(15,23,42,0.82);

    border:
        1px solid
        rgba(255,255,255,0.09);

    border-radius: 20px;

    padding: 30px;

    box-shadow:
        0 25px 70px
        rgba(0,0,0,0.25);

    margin-bottom: 24px;

}


.card-title {

    font-size: 21px;

    margin-bottom: 23px;

}


label {

    display: block;

    color: #cbd5e1;

    font-size: 14px;

    font-weight: 600;

    margin-bottom: 8px;

}


select,
textarea {

    width: 100%;

    border:
        1px solid
        #334155;

    background:
        #080d1c;

    color: white;

    border-radius: 11px;

    padding: 14px;

    outline: none;

    font-size: 15px;

    margin-bottom: 20px;

}


select:focus,
textarea:focus {

    border-color: #4ade80;

    box-shadow:
        0 0 0 3px
        rgba(74,222,128,0.08);

}


textarea {

    min-height: 120px;

    resize: vertical;

}


button {

    width: 100%;

    border: none;

    border-radius: 11px;

    padding: 15px;

    background: #4ade80;

    color: #052e16;

    font-size: 15px;

    font-weight: 800;

    cursor: pointer;

    transition: 0.2s;

}


button:hover {

    transform:
        translateY(-1px);

    box-shadow:
        0 10px 30px
        rgba(74,222,128,0.15);

}


button:disabled {

    opacity: 0.55;

    cursor: not-allowed;

}


/* =====================================================
   RESULT
   ===================================================== */

.result {

    display: none;

    margin-top: 25px;

    border:
        1px solid
        rgba(74,222,128,0.20);

    border-radius: 16px;

    padding: 25px;

    background:
        rgba(4,12,25,0.8);

}


.result-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 15px;

    margin-bottom: 20px;

}


.result-header h2 {

    font-size: 19px;

}


.auth {

    font-size: 11px;

    color: #86efac;

    border:
        1px solid
        rgba(74,222,128,0.3);

    padding:
        5px 9px;

    border-radius: 20px;

}


.decision {

    font-size: 30px;

    font-weight: 900;

    margin-bottom: 8px;

}


.reason {

    color: #a8b3c7;

    line-height: 1.6;

    margin-bottom: 20px;

}


.stats {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 12px;

}


.stat {

    padding: 16px;

    border:
        1px solid
        rgba(255,255,255,0.07);

    border-radius: 12px;

    background:
        rgba(255,255,255,0.025);

}


.stat-label {

    color: #64748b;

    font-size: 11px;

    text-transform: uppercase;

    margin-bottom: 6px;

}


.stat-value {

    font-size: 18px;

    font-weight: 800;

}


/* =====================================================
   SECURITY SECTION
   ===================================================== */

.security-grid {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 14px;

}


.security-item {

    padding: 18px;

    border:
        1px solid
        rgba(255,255,255,0.07);

    border-radius: 13px;

}


.security-icon {

    font-size: 22px;

    margin-bottom: 10px;

}


.security-item h3 {

    font-size: 15px;

    margin-bottom: 7px;

}


.security-item p {

    color: #8190a8;

    font-size: 13px;

    line-height: 1.5;

}


/* =====================================================
   FOOTER
   ===================================================== */

footer {

    text-align: center;

    color: #475569;

    padding: 25px;

    font-size: 12px;

}


/* =====================================================
   MOBILE
   ===================================================== */

@media (max-width: 650px) {

    header {

        padding:
            0 5%;

    }

    .security-badge {

        font-size: 10px;

    }

    .container {

        width: 92%;

        padding-top: 40px;

    }

    .card {

        padding: 20px;

    }

    .stats,
    .security-grid {

        grid-template-columns: 1fr;

    }

    .result-header {

        align-items: flex-start;

        flex-direction: column;

    }

}

</style>

</head>


<body>


<!-- =====================================================
     HEADER
     ===================================================== -->

<header>

    <div class="logo">
        Fin<span>Secure</span> AI
    </div>

    <div class="security-badge">

        <div class="dot"></div>

        ZERO-TRUST ACTIVE

    </div>

</header>


<!-- =====================================================
     MAIN
     ===================================================== -->

<main class="container">


    <!-- HERO -->

    <section class="hero">

        <div class="hero-tag">
            NEURAL NOMADS · FINANCIAL AI
        </div>

        <h1>

            Intelligent Financial

            <br>

            <span>Decision Agent</span>

        </h1>

        <p>

            Analyze financial decisions using
            Zero-Trust authorization, risk analysis,
            and explainable decision making.

        </p>

    </section>


    <!-- QUERY CARD -->

    <section class="card">

        <div class="card-title">
            Ask FinSecure AI
        </div>


        <label for="userId">
            Select User
        </label>


        <select id="userId">

            <option value="U102">
                U102 — Confidential
            </option>

            <option value="U205">
                U205 — Internal
            </option>

            <option value="U301">
                U301 — Restricted
            </option>

        </select>


        <label for="prompt">
            Financial Question
        </label>


        <textarea
            id="prompt"
            placeholder="Example: Can I afford a ₹50000 laptop?"
        ></textarea>


        <button
            id="analyzeBtn"
            onclick="analyze()"
        >

            Analyze Financial Decision

        </button>


        <!-- RESULT -->

        <div
            id="result"
            class="result"
        >

            <div class="result-header">

                <h2>
                    FinSecure Decision
                </h2>

                <div
                    id="auth"
                    class="auth"
                >
                    AUTHORIZED
                </div>

            </div>


            <div
                id="decision"
                class="decision"
            >
                -
            </div>


            <div
                id="reason"
                class="reason"
            >
            </div>


            <div class="stats">


                <div class="stat">

                    <div class="stat-label">
                        Risk Score
                    </div>

                    <div
                        id="risk"
                        class="stat-value"
                    >
                        -
                    </div>

                </div>


                <div class="stat">

                    <div class="stat-label">
                        Savings
                    </div>

                    <div
                        id="savings"
                        class="stat-value"
                    >
                        -
                    </div>

                </div>


                <div class="stat">

                    <div class="stat-label">
                        Disposable Income
                    </div>

                    <div
                        id="disposable"
                        class="stat-value"
                    >
                        -
                    </div>

                </div>


            </div>

        </div>

    </section>


    <!-- HOW IT WORKS -->

    <section class="card">

        <div class="card-title">
            How FinSecure Works
        </div>


        <div class="security-grid">


            <div class="security-item">

                <div class="security-icon">
                    🔐
                </div>

                <h3>
                    Zero-Trust
                </h3>

                <p>

                    Every request is authenticated
                    and checked against the user's
                    clearance level.

                </p>

            </div>


            <div class="security-item">

                <div class="security-icon">
                    📊
                </div>

                <h3>
                    Risk Analysis
                </h3>

                <p>

                    Income, savings, expenses and
                    purchase amount are evaluated
                    before making a decision.

                </p>

            </div>


            <div class="security-item">

                <div class="security-icon">
                    📝
                </div>

                <h3>
                    Audit Trail
                </h3>

                <p>

                    Important authorization and
                    decision events are recorded
                    for accountability.

                </p>

            </div>


        </div>

    </section>


</main>


<!-- =====================================================
     FOOTER
     ===================================================== -->

<footer>

    Neural Nomads · FinSecure AI · Hackathon 2026

</footer>


<!-- =====================================================
     JAVASCRIPT
     ===================================================== -->

<script>

async function analyze() {


    const userId =
        document.getElementById(
            "userId"
        ).value;


    const prompt =
        document.getElementById(
            "prompt"
        ).value.trim();


    const button =
        document.getElementById(
            "analyzeBtn"
        );


    const result =
        document.getElementById(
            "result"
        );


    if (!prompt) {

        alert(
            "Please enter a financial question."
        );

        return;

    }


    button.disabled = true;

    button.innerText =
        "Analyzing...";


    result.style.display =
        "block";


    document.getElementById(
        "decision"
    ).innerText =
        "PROCESSING";


    document.getElementById(
        "reason"
    ).innerText =
        "Checking Zero-Trust authorization and analyzing financial data...";


    try {


        const response =
            await fetch(
                "/query",
                {

                    method:
                        "POST",

                    headers:
                        {
                            "Content-Type":
                                "application/json"
                        },

                    body:
                        JSON.stringify(
                            {
                                user_id:
                                    userId,

                                prompt:
                                    prompt
                            }
                        )

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Server request failed."
            );

        }


        document.getElementById(
            "decision"
        ).innerText =
            data.decision ||
            "UNKNOWN";


        document.getElementById(
            "reason"
        ).innerText =
            data.reason ||
            "No explanation available.";


        document.getElementById(
            "risk"
        ).innerText =
            (
                data.risk_score ??
                "-"
            ) + "/100";


        const summary =
            data.financial_summary ||
            {};


        document.getElementById(
            "savings"
        ).innerText =
            "₹" +
            (
                summary.savings ??
                "-"
            );


        document.getElementById(
            "disposable"
        ).innerText =
            "₹" +
            (
                summary.disposable_income ??
                "-"
            );


        const auth =
            document.getElementById(
                "auth"
            );


        if (
            data.security &&
            data.security.authorization
        ) {

            auth.innerText =
                data.security.authorization
                    .toUpperCase();

        }


    }


    catch (error) {


        document.getElementById(
            "decision"
        ).innerText =
            "ERROR";


        document.getElementById(
            "reason"
        ).innerText =
            error.message;


        document.getElementById(
            "risk"
        ).innerText =
            "-";


        document.getElementById(
            "savings"
        ).innerText =
            "-";


        document.getElementById(
            "disposable"
        ).innerText =
            "-";

    }


    finally {

        button.disabled =
            false;

        button.innerText =
            "Analyze Financial Decision";

    }

}

</script>


</body>

</html>
"""


# =========================================================
# ROOT PAGE
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def home():

    return HTML_PAGE


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {

        "status": "online",

        "service": "FinSecure AI",

        "team": "Neural Nomads",

        "message":
            "FinSecure AI is running successfully."

    }


# =========================================================
# QUERY API
# =========================================================

@app.post("/query")
def query(
    request: QueryRequest
):

    try:

        return agent.process_query(
            request.user_id,
            request.prompt
        )

    except Exception as exc:

        logger.exception(
            "Query processing failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# =========================================================
# AUDIT API
# =========================================================

@app.get("/audit")
def get_audit_logs():

    return {

        "count":
            len(AUDIT_LOG),

        "logs":
            AUDIT_LOG

    }


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
