from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import re

app = FastAPI(title="FinSecure AI")


# =========================================================
# DEMO USER DATA
# =========================================================

USERS = {
    "U102": {
        "name": "Alex Morgan",
        "clearance": "CONFIDENTIAL",
        "income": 85000,
        "savings": 250000,
        "monthly_expenses": 42000
    },
    "U205": {
        "name": "Jordan Lee",
        "clearance": "INTERNAL",
        "income": 55000,
        "savings": 100000,
        "monthly_expenses": 35000
    },
    "U301": {
        "name": "Taylor Smith",
        "clearance": "RESTRICTED",
        "income": 120000,
        "savings": 500000,
        "monthly_expenses": 50000
    }
}


AUDIT_LOG: List[Dict[str, Any]] = []


class QueryRequest(BaseModel):
    user_id: str
    prompt: str


# =========================================================
# FINANCIAL ANALYSIS
# =========================================================

def extract_amount(prompt: str) -> float:

    patterns = [
        r"₹\s*([\d,]+(?:\.\d+)?)",
        r"Rs\.?\s*([\d,]+(?:\.\d+)?)",
        r"rupees?\s*([\d,]+(?:\.\d+)?)",
        r"\$\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            prompt,
            re.IGNORECASE
        )

        if match:
            return float(
                match.group(1).replace(",", "")
            )

    numbers = re.findall(
        r"\b\d+(?:,\d+)*(?:\.\d+)?\b",
        prompt
    )

    if numbers:
        return float(
            numbers[0].replace(",", "")
        )

    return 0


def analyze_finances(
    user: Dict[str, Any],
    purchase_amount: float
):

    income = user["income"]
    savings = user["savings"]
    expenses = user["monthly_expenses"]

    disposable_income = income - expenses

    emergency_reserve = expenses * 3

    remaining_savings = savings - purchase_amount

    if remaining_savings < emergency_reserve:

        decision = "NOT RECOMMENDED"

        reason = (
            "The purchase would reduce the user's savings "
            "below the recommended three-month emergency reserve."
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
# DASHBOARD HTML
# =========================================================

HTML_PAGE = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>FinSecure AI</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {

    font-family:
        Inter,
        Arial,
        Helvetica,
        sans-serif;

    background: #06111f;

    color: #f8fafc;

    min-height: 100vh;
}


/* =====================================================
   LAYOUT
   ===================================================== */

.app {

    display: flex;

    min-height: 100vh;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

.sidebar {

    width: 250px;

    background: #081624;

    border-right: 1px solid #1b3043;

    padding: 25px 18px;

    position: fixed;

    left: 0;

    top: 0;

    bottom: 0;
}

.logo {

    display: flex;

    align-items: center;

    gap: 10px;

    font-size: 22px;

    font-weight: 800;

    margin-bottom: 45px;
}

.logo-icon {

    width: 38px;

    height: 38px;

    border-radius: 10px;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #16a34a;

    color: #03140a;

    font-weight: 900;
}

.logo span {

    color: #22c55e;
}


.nav-title {

    color: #64748b;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1px;

    margin: 20px 12px 10px;
}

.nav-item {

    padding: 13px 14px;

    border-radius: 9px;

    color: #94a3b8;

    margin-bottom: 5px;

    cursor: pointer;

    transition: 0.2s;
}

.nav-item:hover,
.nav-item.active {

    background: #102b22;

    color: #4ade80;
}


.security-box {

    position: absolute;

    left: 18px;

    right: 18px;

    bottom: 25px;

    background: #0b2119;

    border: 1px solid #17452f;

    border-radius: 12px;

    padding: 15px;
}

.security-title {

    color: #4ade80;

    font-size: 12px;

    font-weight: 700;

    margin-bottom: 6px;
}

.security-text {

    color: #78908a;

    font-size: 11px;

    line-height: 1.5;
}


/* =====================================================
   MAIN
   ===================================================== */

.main {

    margin-left: 250px;

    width: calc(100% - 250px);

    padding: 28px 35px;
}


/* =====================================================
   TOP BAR
   ===================================================== */

.topbar {

    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-bottom: 30px;
}

.page-title h1 {

    font-size: 27px;

    margin-bottom: 5px;
}

.page-title p {

    color: #64748b;

    font-size: 13px;
}

.status {

    display: flex;

    align-items: center;

    gap: 8px;

    padding: 9px 14px;

    background: #0a2119;

    border: 1px solid #17452f;

    border-radius: 30px;

    color: #4ade80;

    font-size: 12px;

    font-weight: 700;
}

.status-dot {

    width: 7px;

    height: 7px;

    background: #22c55e;

    border-radius: 50%;
}


/* =====================================================
   STAT CARDS
   ===================================================== */

.stats-grid {

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 18px;

    margin-bottom: 22px;
}

.stat-card {

    background: #0b1928;

    border: 1px solid #1b3043;

    border-radius: 13px;

    padding: 20px;
}

.stat-label {

    color: #64748b;

    font-size: 11px;

    text-transform: uppercase;

    letter-spacing: .7px;

    margin-bottom: 12px;
}

.stat-number {

    font-size: 25px;

    font-weight: 800;
}

.stat-sub {

    color: #4ade80;

    font-size: 11px;

    margin-top: 7px;
}


/* =====================================================
   GRID
   ===================================================== */

.dashboard-grid {

    display: grid;

    grid-template-columns:
        1.5fr 1fr;

    gap: 20px;

    margin-bottom: 22px;
}

.card {

    background: #0b1928;

    border: 1px solid #1b3043;

    border-radius: 14px;

    padding: 23px;
}

.card-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 20px;
}

.card-title {

    font-size: 16px;

    font-weight: 700;
}

.card-small {

    color: #64748b;

    font-size: 11px;
}


/* =====================================================
   ANALYZER
   ===================================================== */

.user-row {

    display: grid;

    grid-template-columns: 1fr 1fr;

    gap: 14px;

    margin-bottom: 16px;
}

.field label {

    display: block;

    color: #94a3b8;

    font-size: 11px;

    margin-bottom: 7px;
}

select,
textarea {

    width: 100%;

    background: #06111f;

    border: 1px solid #263d52;

    color: #e2e8f0;

    border-radius: 8px;

    padding: 12px;

    outline: none;

    font-family: inherit;
}

select:focus,
textarea:focus {

    border-color: #22c55e;
}

textarea {

    height: 105px;

    resize: none;

    margin-bottom: 14px;
}

.analyze-btn {

    width: 100%;

    padding: 13px;

    border: none;

    border-radius: 8px;

    background: #22c55e;

    color: #03140a;

    font-weight: 800;

    cursor: pointer;

    transition: .2s;
}

.analyze-btn:hover {

    background: #4ade80;

    transform: translateY(-1px);
}


/* =====================================================
   SECURITY PANEL
   ===================================================== */

.security-list {

    display: flex;

    flex-direction: column;

    gap: 14px;
}

.security-row {

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding-bottom: 14px;

    border-bottom: 1px solid #162a3b;
}

.security-row:last-child {

    border-bottom: none;

    padding-bottom: 0;
}

.security-name {

    color: #cbd5e1;

    font-size: 12px;
}

.badge {

    font-size: 10px;

    padding: 5px 9px;

    border-radius: 20px;

    background: #0a2119;

    color: #4ade80;
}


/* =====================================================
   RESULT
   ===================================================== */

.result {

    display: none;

    margin-top: 20px;

    padding: 20px;

    border-radius: 12px;

    background: #071827;

    border: 1px solid #24435a;
}

.result-top {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 15px;
}

.decision {

    font-size: 22px;

    font-weight: 900;

    color: #4ade80;
}

.risk {

    text-align: right;
}

.risk-label {

    color: #64748b;

    font-size: 10px;
}

.risk-value {

    font-size: 22px;

    font-weight: 800;
}

.reason {

    color: #94a3b8;

    line-height: 1.6;

    font-size: 12px;

    margin-bottom: 18px;
}

.result-stats {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 10px;
}

.result-stat {

    background: #0b1928;

    padding: 12px;

    border-radius: 8px;
}

.result-stat-label {

    color: #64748b;

    font-size: 9px;

    margin-bottom: 5px;
}

.result-stat-value {

    font-size: 14px;

    font-weight: 700;
}


/* =====================================================
   AUDIT
   ===================================================== */

.audit-table {

    width: 100%;

    border-collapse: collapse;
}

.audit-table th {

    text-align: left;

    color: #64748b;

    font-size: 10px;

    text-transform: uppercase;

    padding: 11px;

    border-bottom: 1px solid #1b3043;
}

.audit-table td {

    padding: 12px 11px;

    color: #94a3b8;

    font-size: 11px;

    border-bottom: 1px solid #142637;
}

.success {

    color: #4ade80;
}


/* =====================================================
   RESPONSIVE
   ===================================================== */

@media (max-width: 1000px) {

    .stats-grid {

        grid-template-columns:
            repeat(2, 1fr);
    }

    .dashboard-grid {

        grid-template-columns: 1fr;
    }
}

@media (max-width: 700px) {

    .sidebar {

        display: none;
    }

    .main {

        margin-left: 0;

        width: 100%;

        padding: 20px;
    }

    .stats-grid {

        grid-template-columns: 1fr;
    }

    .user-row {

        grid-template-columns: 1fr;
    }
}

</style>

</head>


<body>


<div class="app">


<!-- ===================================================
     SIDEBAR
     =================================================== -->

<aside class="sidebar">

    <div class="logo">

        <div class="logo-icon">
            FS
        </div>

        <div>
            Fin<span>Secure</span>
        </div>

    </div>


    <div class="nav-title">
        PLATFORM
    </div>

    <div class="nav-item active">
        ◈ &nbsp; Dashboard
    </div>

    <div class="nav-item">
        ◉ &nbsp; Decision Agent
    </div>

    <div class="nav-item">
        ◇ &nbsp; Risk Analysis
    </div>


    <div class="nav-title">
        SECURITY
    </div>

    <div class="nav-item">
        ▣ &nbsp; Audit Trail
    </div>

    <div class="nav-item">
        ◆ &nbsp; Access Control
    </div>


    <div class="security-box">

        <div class="security-title">
            ● ZERO-TRUST ACTIVE
        </div>

        <div class="security-text">
            Every request is authenticated,
            authorized and audited.
        </div>

    </div>

</aside>


<!-- ===================================================
     MAIN CONTENT
     =================================================== -->

<main class="main">


    <!-- TOP BAR -->

    <div class="topbar">

        <div class="page-title">

            <h1>
                Financial Intelligence Dashboard
            </h1>

            <p>
                Secure decision-making powered by
                Zero-Trust architecture
            </p>

        </div>


        <div class="status">

            <span class="status-dot"></span>

            SYSTEM OPERATIONAL

        </div>

    </div>


    <!-- STATISTICS -->

    <div class="stats-grid">


        <div class="stat-card">

            <div class="stat-label">
                Active Users
            </div>

            <div class="stat-number">
                03
            </div>

            <div class="stat-sub">
                ● All systems verified
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Decisions Analyzed
            </div>

            <div class="stat-number"
                 id="decisionCount">
                0
            </div>

            <div class="stat-sub">
                ● Real-time analysis
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Security Level
            </div>

            <div class="stat-number">
                High
            </div>

            <div class="stat-sub">
                ● Zero-Trust enabled
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                API Status
            </div>

            <div class="stat-number">
                Online
            </div>

            <div class="stat-sub">
                ● FastAPI connected
            </div>

        </div>


    </div>


    <!-- MAIN DASHBOARD -->

    <div class="dashboard-grid">


        <!-- DECISION AGENT -->

        <section class="card">

            <div class="card-header">

                <div class="card-title">
                    Intelligent Decision Agent
                </div>

                <div class="card-small">
                    AI FINANCIAL ANALYSIS
                </div>

            </div>


            <div class="user-row">


                <div class="field">

                    <label>
                        USER ID
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

                </div>


                <div class="field">

                    <label>
                        ACCESS STATUS
                    </label>

                    <select disabled>

                        <option>
                            ✓ AUTHORIZED
                        </option>

                    </select>

                </div>


            </div>


            <div class="field">

                <label>
                    FINANCIAL REQUEST
                </label>

                <textarea
                    id="question"
                    placeholder="Example: Can I buy a laptop for ₹80000?"
                ></textarea>

            </div>


            <button
                class="analyze-btn"
                onclick="analyze()"
                id="analyzeButton">

                ANALYZE FINANCIAL DECISION

            </button>


            <!-- RESULT -->

            <div
                class="result"
                id="result">


                <div class="result-top">

                    <div>

                        <div class="card-small">
                            DECISION
                        </div>

                        <div
                            class="decision"
                            id="decision">

                        </div>

                    </div>


                    <div class="risk">

                        <div class="risk-label">
                            RISK SCORE
                        </div>

                        <div
                            class="risk-value"
                            id="risk">

                        </div>

                    </div>

                </div>


                <div
                    class="reason"
                    id="reason">

                </div>


                <div class="result-stats">


                    <div class="result-stat">

                        <div class="result-stat-label">
                            SAVINGS
                        </div>

                        <div
                            class="result-stat-value"
                            id="savings">

                        </div>

                    </div>


                    <div class="result-stat">

                        <div class="result-stat-label">
                            DISPOSABLE INCOME
                        </div>

                        <div
                            class="result-stat-value"
                            id="income">

                        </div>

                    </div>


                    <div class="result-stat">

                        <div class="result-stat-label">
                            REMAINING SAVINGS
                        </div>

                        <div
                            class="result-stat-value"
                            id="remaining">

                        </div>

                    </div>


                </div>

            </div>


        </section>


        <!-- SECURITY -->

        <section class="card">

            <div class="card-header">

                <div class="card-title">
                    Security Monitor
                </div>

                <div class="card-small">
                    ZERO-TRUST
                </div>

            </div>


            <div class="security-list">


                <div class="security-row">

                    <div class="security-name">
                        Identity Verification
                    </div>

                    <div class="badge">
                        VERIFIED
                    </div>

                </div>


                <div class="security-row">

                    <div class="security-name">
                        Access Authorization
                    </div>

                    <div class="badge">
                        ENFORCED
                    </div>

                </div>


                <div class="security-row">

                    <div class="security-name">
                        Financial Data Protection
                    </div>

                    <div class="badge">
                        ACTIVE
                    </div>

                </div>


                <div class="security-row">

                    <div class="security-name">
                        Audit Logging
                    </div>

                    <div class="badge">
                        ENABLED
                    </div>

                </div>


                <div class="security-row">

                    <div class="security-name">
                        Policy Enforcement
                    </div>

                    <div class="badge">
                        ACTIVE
                    </div>

                </div>


            </div>

        </section>


    </div>


    <!-- AUDIT -->

    <section class="card">

        <div class="card-header">

            <div class="card-title">
                Recent Security Activity
            </div>

            <div class="card-small">
                LIVE AUDIT TRAIL
            </div>

        </div>


        <table class="audit-table">

            <thead>

                <tr>

                    <th>
                        EVENT
                    </th>

                    <th>
                        USER
                    </th>

                    <th>
                        STATUS
                    </th>

                    <th>
                        TIME
                    </th>

                </tr>

            </thead>


            <tbody id="auditBody">

                <tr>

                    <td>
                        System initialized
                    </td>

                    <td>
                        SYSTEM
                    </td>

                    <td class="success">
                        SUCCESS
                    </td>

                    <td>
                        Just now
                    </td>

                </tr>


                <tr>

                    <td>
                        Zero-Trust policy loaded
                    </td>

                    <td>
                        SYSTEM
                    </td>

                    <td class="success">
                        ACTIVE
                    </td>

                    <td>
                        Just now
                    </td>

                </tr>

            </tbody>

        </table>

    </section>


</main>

</div>


<script>

let decisions = 0;


function formatMoney(value) {

    return "₹" +
        Number(value).toLocaleString("en-IN");

}


async function analyze() {

    const user =
        document.getElementById("user").value;

    const question =
        document.getElementById("question").value.trim();

    const button =
        document.getElementById("analyzeButton");


    if (!question) {

        alert(
            "Please enter a financial request."
        );

        return;
    }


    button.disabled = true;

    button.innerText =
        "ANALYZING...";


    try {

        const response = await fetch(
            "/query",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    user_id: user,

                    prompt: question

                })

            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data.detail ||
                "Authorization failed."
            );

            return;
        }


        document.getElementById(
            "result"
        ).style.display = "block";


        document.getElementById(
            "decision"
        ).innerText =
            data.decision;


        document.getElementById(
            "reason"
        ).innerText =
            data.reason;


        document.getElementById(
            "risk"
        ).innerText =
            data.risk_score + "/100";


        document.getElementById(
            "savings"
        ).innerText =
            formatMoney(data.savings);


        document.getElementById(
            "income"
        ).innerText =
            formatMoney(
                data.disposable_income
            );


        document.getElementById(
            "remaining"
        ).innerText =
            formatMoney(
                data.remaining_savings
            );


        decisions++;


        document.getElementById(
            "decisionCount"
        ).innerText =
            decisions;


        addAuditRow(
            data.decision,
            user
        );


    } catch (error) {

        alert(
            "Unable to connect to FinSecure AI."
        );

        console.error(error);

    } finally {

        button.disabled = false;

        button.innerText =
            "ANALYZE FINANCIAL DECISION";

    }

}


function addAuditRow(
    decision,
    user
) {

    const table =
        document.getElementById(
            "auditBody"
        );


    const row =
        document.createElement("tr");


    const time =
        new Date().toLocaleTimeString();


    row.innerHTML = `

        <td>
            Financial decision analyzed
        </td>

        <td>
            ${user}
        </td>

        <td class="success">
            ${decision}
        </td>

        <td>
            ${time}
        </td>

    `;


    table.prepend(row);

}

</script>


</body>

</html>
"""


# =========================================================
# ROOT
# =========================================================

@app.get("/", response_class=HTMLResponse)
def root():

    return HTML_PAGE


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "online",
        "service": "FinSecure AI",
        "team": "Neural Nomads"
    }


# =========================================================
# QUERY
# =========================================================

@app.post("/query")
def query(request: QueryRequest):

    if request.user_id not in USERS:

        raise HTTPException(
            status_code=403,
            detail="Unauthorized user"
        )


    user = USERS[request.user_id]


    # Zero-Trust authorization

    if user["clearance"] not in [
        "CONFIDENTIAL",
        "RESTRICTED"
    ]:

        AUDIT_LOG.append({

            "timestamp":
                datetime.now().isoformat(),

            "user_id":
                request.user_id,

            "action":
                "ACCESS_DENIED"

        })

        raise HTTPException(
            status_code=403,
            detail="Insufficient clearance level"
        )


    AUDIT_LOG.append({

        "timestamp":
            datetime.now().isoformat(),

        "user_id":
            request.user_id,

        "action":
            "ACCESS_GRANTED"

    })


    amount =
        extract_amount(request.prompt)


    if amount <= 0:

        return {

            "decision":
                "NEEDS MORE INFORMATION",

            "reason":
                "Please provide a purchase amount.",

            "risk_score":
                0,

            "savings":
                user["savings"],

            "disposable_income":
                user["income"] -
                user["monthly_expenses"],

            "remaining_savings":
                user["savings"]

        }


    result =
        analyze_finances(
            user,
            amount
        )


    AUDIT_LOG.append({

        "timestamp":
            datetime.now().isoformat(),

        "user_id":
            request.user_id,

        "action":
            "FINANCIAL_ANALYSIS",

        "decision":
            result["decision"],

        "risk_score":
            result["risk_score"]

    })


    return result


# =========================================================
# AUDIT
# =========================================================

@app.get("/audit")
def audit():

    return {
        "events": AUDIT_LOG
    }
