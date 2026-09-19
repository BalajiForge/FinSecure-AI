from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import re

app = FastAPI(title="FinSecure AI")


# =========================================================
# ZERO-TRUST CLEARANCE LEVELS
# =========================================================

CLEARANCE_RANKS = {
    "PUBLIC": 0,
    "INTERNAL": 1,
    "CONFIDENTIAL": 2,
    "RESTRICTED": 3
}


# =========================================================
# DEMO FINANCIAL USERS
# =========================================================

USERS = {
    "U102": {
        "clearance": "CONFIDENTIAL",
        "income": 85000,
        "savings": 250000,
        "monthly_expenses": 42000
    },
    "U205": {
        "clearance": "INTERNAL",
        "income": 55000,
        "savings": 100000,
        "monthly_expenses": 35000
    },
    "U301": {
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


# =========================================================
# REQUEST MODEL
# =========================================================

class QueryRequest(BaseModel):
    user_id: str
    prompt: str


# =========================================================
# ZERO-TRUST AUTHORIZATION
# =========================================================

def authorize_user(user_id: str) -> Dict[str, Any]:

    if user_id not in USERS:
        AUDIT_LOG.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": "ACCESS_DENIED",
            "reason": "Unknown user"
        })

        raise HTTPException(
            status_code=403,
            detail="Unauthorized user"
        )

    user = USERS[user_id]

    clearance = user["clearance"]

    if CLEARANCE_RANKS[clearance] < CLEARANCE_RANKS["CONFIDENTIAL"]:

        AUDIT_LOG.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": "ACCESS_DENIED",
            "reason": "Insufficient clearance"
        })

        raise HTTPException(
            status_code=403,
            detail="Insufficient clearance level"
        )

    AUDIT_LOG.append({
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "action": "ACCESS_GRANTED",
        "clearance": clearance
    })

    return user


# =========================================================
# EXTRACT PURCHASE AMOUNT
# =========================================================

def extract_amount(prompt: str) -> float:

    patterns = [
        r"₹\s*([\d,]+(?:\.\d+)?)",
        r"Rs\.?\s*([\d,]+(?:\.\d+)?)",
        r"rupees?\s*([\d,]+(?:\.\d+)?)",
        r"\$\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)

        if match:
            return float(match.group(1).replace(",", ""))

    numbers = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", prompt)

    if numbers:
        return float(numbers[0].replace(",", ""))

    return 0


# =========================================================
# FINANCIAL ANALYSIS
# =========================================================

def analyze_finances(
    user: Dict[str, Any],
    purchase_amount: float
) -> Dict[str, Any]:

    income = user["income"]
    savings = user["savings"]
    expenses = user["monthly_expenses"]

    disposable_income = income - expenses

    emergency_reserve = expenses * 3

    remaining_savings = savings - purchase_amount

    if remaining_savings < emergency_reserve:

        decision = "NOT RECOMMENDED"

        reason = (
            "The purchase would reduce savings below the "
            "recommended three-month emergency reserve."
        )

        risk_score = 85

    elif purchase_amount <= disposable_income * 3:

        decision = "APPROVED"

        reason = (
            "The purchase is within the user's estimated "
            "financial capacity while maintaining the emergency reserve."
        )

        risk_score = 20

    else:

        decision = "HIGH RISK"

        reason = (
            "The purchase is large compared with the user's "
            "available disposable income."
        )

        risk_score = 70

    return {
        "decision": decision,
        "reason": reason,
        "risk_score": risk_score,
        "income": income,
        "savings": savings,
        "monthly_expenses": expenses,
        "disposable_income": disposable_income,
        "emergency_reserve": emergency_reserve,
        "purchase_amount": purchase_amount,
        "remaining_savings": remaining_savings
    }


# =========================================================
# CONFLICT RESOLUTION
# =========================================================

def resolve_conflict(prompt: str) -> str:

    positive_words = [
        "afford",
        "buy",
        "purchase",
        "good",
        "okay",
        "yes"
    ]

    risk_words = [
        "debt",
        "loan",
        "emergency",
        "risk",
        "danger",
        "borrow"
    ]

    lower_prompt = prompt.lower()

    has_positive = any(word in lower_prompt for word in positive_words)

    has_risk = any(word in lower_prompt for word in risk_words)

    if has_positive and has_risk:
        return (
            "Safety rules take priority because the request "
            "contains conflicting financial-risk signals."
        )

    return ""


# =========================================================
# FRONTEND
# =========================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FinSecure AI</title>

<style>

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    background: #07111f;
    color: #ffffff;
    min-height: 100vh;
}

.container {
    width: 90%;
    max-width: 1150px;
    margin: auto;
}

/* HEADER */

header {
    border-bottom: 1px solid #1d3447;
    padding: 22px 0;
}

.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 24px;
    font-weight: bold;
}

.logo span {
    color: #22c55e;
}

.status {
    background: rgba(34,197,94,0.12);
    color: #4ade80;
    padding: 8px 14px;
    border-radius: 20px;
    font-size: 13px;
}

/* HERO */

.hero {
    text-align: center;
    padding: 70px 20px 40px;
}

.hero h1 {
    font-size: 48px;
    margin-bottom: 15px;
}

.hero h1 span {
    color: #22c55e;
}

.hero p {
    color: #9fb0c0;
    font-size: 18px;
}

/* MAIN CARD */

.card {
    background: #0c1b2a;
    border: 1px solid #1d3447;
    border-radius: 18px;
    padding: 30px;
    margin-top: 25px;
}

.card h2 {
    margin-bottom: 8px;
}

.subtitle {
    color: #8da0b2;
    margin-bottom: 25px;
}

/* FORM */

label {
    display: block;
    margin-bottom: 8px;
    color: #cbd5e1;
    font-weight: bold;
}

select,
textarea {
    width: 100%;
    background: #07111f;
    border: 1px solid #29445a;
    color: white;
    border-radius: 10px;
    padding: 14px;
    font-size: 15px;
    margin-bottom: 20px;
}

textarea {
    min-height: 120px;
    resize: vertical;
}

button {
    width: 100%;
    padding: 15px;
    border: none;
    border-radius: 10px;
    background: #22c55e;
    color: #04100a;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #4ade80;
}

/* RESULT */

.result {
    display: none;
    margin-top: 25px;
    background: #07111f;
    border: 1px solid #29445a;
    border-radius: 15px;
    padding: 25px;
}

.decision {
    font-size: 30px;
    font-weight: bold;
    color: #4ade80;
    margin-bottom: 12px;
}

.reason {
    color: #b5c4d1;
    line-height: 1.6;
    margin-bottom: 25px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

.stat {
    background: #0c1b2a;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #1d3447;
}

.stat-title {
    color: #8195a7;
    font-size: 12px;
    margin-bottom: 8px;
}

.stat-value {
    font-size: 20px;
    font-weight: bold;
}

/* FEATURES */

.features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin: 40px 0 70px;
}

.feature {
    background: #0c1b2a;
    border: 1px solid #1d3447;
    border-radius: 15px;
    padding: 25px;
}

.feature h3 {
    margin-bottom: 10px;
    color: #4ade80;
}

.feature p {
    color: #8da0b2;
    line-height: 1.5;
}

/* RESPONSIVE */

@media (max-width: 800px) {

    .hero h1 {
        font-size: 36px;
    }

    .stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .features {
        grid-template-columns: 1fr;
    }
}

</style>

</head>

<body>

<header>

<div class="container nav">

<div class="logo">
Fin<span>Secure</span> AI
</div>

<div class="status">
● ZERO-TRUST ACTIVE
</div>

</div>

</header>


<main class="container">

<section class="hero">

<h1>
Intelligent <span>Financial Decisions.</span>
</h1>

<p>
Secure. Explainable. Zero-Trust powered.
</p>

</section>


<section class="card">

<h2>Financial Decision Agent</h2>

<p class="subtitle">
Ask FinSecure AI whether a financial decision is safe.
</p>


<label for="user">
Select User
</label>

<select id="user">

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


<label for="question">
Financial Question
</label>

<textarea
id="question"
placeholder="Example: Can I buy a laptop for ₹80000?"
></textarea>


<button onclick="analyze()">
ANALYZE DECISION
</button>


<div class="result" id="result">

<div class="decision" id="decision">
</div>

<div class="reason" id="reason">
</div>


<div class="stats">

<div class="stat">

<div class="stat-title">
RISK SCORE
</div>

<div class="stat-value" id="risk">
-
</div>

</div>


<div class="stat">

<div class="stat-title">
SAVINGS
</div>

<div class="stat-value" id="savings">
-
</div>

</div>


<div class="stat">

<div class="stat-title">
DISPOSABLE INCOME
</div>

<div class="stat-value" id="income">
-
</div>

</div>


<div class="stat">

<div class="stat-title">
REMAINING SAVINGS
</div>

<div class="stat-value" id="remaining">
-
</div>

</div>

</div>

</div>

</section>


<section class="features">

<div class="feature">

<h3>Zero-Trust</h3>

<p>
Every request is authenticated and authorized before
financial information is accessed.
</p>

</div>


<div class="feature">

<h3>Risk Analysis</h3>

<p>
The system evaluates income, expenses, savings,
emergency reserves and purchase amount.
</p>

</div>


<div class="feature">

<h3>Audit Trail</h3>

<p>
Important authorization and decision events are
recorded for transparency.
</p>

</div>

</section>

</main>


<script>

async function analyze() {

    const user_id =
        document.getElementById("user").value;

    const prompt =
        document.getElementById("question").value;

    if (!prompt.trim()) {

        alert("Please enter a financial question.");

        return;
    }


    const button =
        document.querySelector("button");

    button.innerText = "ANALYZING...";

    button.disabled = true;


    try {

        const response = await fetch("/query", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                user_id: user_id,
                prompt: prompt
            })

        });


        const data = await response.json();


        if (!response.ok) {

            alert(data.detail || "Request failed.");

            return;
        }


        document.getElementById("result").style.display = "block";

        document.getElementById("decision").innerText =
            data.decision;

        document.getElementById("reason").innerText =
            data.reason;

        document.getElementById("risk").innerText =
            data.risk_score + "/100";

        document.getElementById("savings").innerText =
            "₹" + Number(data.savings).toLocaleString("en-IN");

        document.getElementById("income").innerText =
            "₹" + Number(data.disposable_income).toLocaleString("en-IN");

        document.getElementById("remaining").innerText =
            "₹" + Number(data.remaining_savings).toLocaleString("en-IN");

    }

    catch (error) {

        alert("Unable to connect to FinSecure AI.");

        console.error(error);

    }

    finally {

        button.innerText = "ANALYZE DECISION";

        button.disabled = false;

    }

}

</script>

</body>

</html>
"""


# =========================================================
# ROOT PAGE
# =========================================================

@app.get("/", response_class=HTMLResponse)
def root():

    return HTML_PAGE


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "online",
        "service": "FinSecure AI",
        "team": "Neural Nomads"
    }


# =========================================================
# FINANCIAL QUERY
# =========================================================

@app.post("/query")
def query(request: QueryRequest):

    user = authorize_user(request.user_id)

    amount = extract_amount(request.prompt)

    if amount <= 0:

        return {
            "decision": "NEEDS MORE INFORMATION",
            "reason": "Please provide the purchase amount.",
            "risk_score": 0,
            "savings": user["savings"],
            "disposable_income":
                user["income"] - user["monthly_expenses"],
            "remaining_savings": user["savings"]
        }


    conflict_message = resolve_conflict(request.prompt)

    result = analyze_finances(
        user,
        amount
    )


    if conflict_message:

        result["reason"] = (
            result["reason"] +
            " " +
            conflict_message
        )


    AUDIT_LOG.append({

        "timestamp": datetime.now().isoformat(),

        "user_id": request.user_id,

        "action": "FINANCIAL_ANALYSIS",

        "purchase_amount": amount,

        "decision": result["decision"],

        "risk_score": result["risk_score"]

    })


    return result


# =========================================================
# AUDIT ENDPOINT
# =========================================================

@app.get("/audit")
def audit():

    return {
        "events": AUDIT_LOG
    }

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_PAGE
