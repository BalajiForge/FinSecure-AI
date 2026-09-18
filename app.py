"""
FinSecure AI: Unified Zero-Trust Enterprise Financial & Decision Agent
Team: Neural Nomads
Members: Balaji A, Anish, Sanjay, Ashrith, Jeevan
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("FinSecureAgent")


# =========================================================
# CUSTOM EXCEPTIONS
# =========================================================

class FinSecureException(Exception):
    """Base exception for the FinSecure agent."""
    pass


class AuthenticationError(FinSecureException):
    """Raised when user profile or security clearance fails validation."""
    pass


class DataIntegrityError(FinSecureException):
    """Raised when incoming documents or payloads are malformed."""
    pass


class FinancialLogicError(FinSecureException):
    """Raised when financial processing fails."""
    pass


# =========================================================
# SECURITY CLEARANCE
# =========================================================

CLEARANCE_RANKS: Dict[str, int] = {
    "PUBLIC": 0,
    "INTERNAL": 1,
    "CONFIDENTIAL": 2,
    "RESTRICTED": 3,
}


# =========================================================
# FINSECURE AGENT
# =========================================================

class FinSecureAgent:
    """
    FinSecure AI handles:

    1. Zero-Trust document authorization
    2. Document conflict resolution
    3. Financial expense tracking
    4. Budget analysis
    5. Financial decision analysis
    6. Audit logging
    """

    def __init__(self) -> None:

        self.audit_log: List[Dict[str, Any]] = []

        self.user_financial_profiles: Dict[str, Dict[str, Any]] = {

            "U102": {
                "monthly_budget": 8000.0,
                "expenses": {
                    "Food": 12000.0,
                    "Fuel": 1200.0,
                    "Utilities": 2500.0,
                },
                "savings_goal": {
                    "name": "Trip to Goa",
                    "target": 20000.0,
                    "current": 14000.0,
                },
                "liquid_cash": 18000.0,
            },

            "U205": {
                "monthly_budget": 15000.0,
                "expenses": {
                    "Food": 6000.0,
                    "Entertainment": 3000.0,
                },
                "savings_goal": {
                    "name": "Emergency Fund",
                    "target": 50000.0,
                    "current": 15000.0,
                },
                "liquid_cash": 25000.0,
            },

            "U301": {
                "monthly_budget": 50000.0,
                "expenses": {
                    "Food": 10000.0,
                    "Investment": 15000.0,
                },
                "savings_goal": {
                    "name": "Portfolio Expansion",
                    "target": 100000.0,
                    "current": 45000.0,
                },
                "liquid_cash": 60000.0,
            },
        }

    # =====================================================
    # PII MASKING
    # =====================================================

    @staticmethod
    def mask_pii(text: str) -> str:

        if not isinstance(text, str):
            return str(text)

        try:

            # Indian phone numbers
            text = re.sub(
                r"\b[6-9]\d{9}\b",
                "[MASKED_PHONE]",
                text,
            )

            # PAN numbers
            text = re.sub(
                r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
                "[MASKED_PAN]",
                text,
                flags=re.I,
            )

            # Credit/debit card numbers
            text = re.sub(
                r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
                "[MASKED_CARD]",
                text,
            )

            return text

        except Exception as e:

            logger.error(f"Failed to mask PII: {e}")

            return text

    # =====================================================
    # DOCUMENT AUTHORIZATION
    # =====================================================

    def authorize_documents(
        self,
        user: Dict[str, Any],
        documents: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:

        if not isinstance(user, dict):
            raise AuthenticationError(
                "User context must be a valid dictionary."
            )

        if not isinstance(documents, list):
            raise DataIntegrityError(
                "Documents must be provided as a list."
            )

        user_role = str(
            user.get("role", "")
        ).strip().upper()

        user_dept = str(
            user.get("department", "")
        ).strip().upper()

        user_clearance = str(
            user.get("clearance", "PUBLIC")
        ).strip().upper()

        user_rank = CLEARANCE_RANKS.get(
            user_clearance,
            0,
        )

        authorized_docs: List[Dict[str, Any]] = []
        blocked_docs: List[Dict[str, Any]] = []

        for doc in documents:

            try:

                if not isinstance(doc, dict):
                    blocked_docs.append({
                        "document_id": "INVALID_DOC",
                        "reason": "Document must be a dictionary.",
                    })
                    continue

                doc_id = doc.get(
                    "document_id",
                    "UNKNOWN_DOC",
                )

                doc_class = str(
                    doc.get(
                        "classification",
                        "RESTRICTED",
                    )
                ).strip().upper()

                doc_rank = CLEARANCE_RANKS.get(
                    doc_class,
                    999,
                )

                allowed_departments = doc.get(
                    "allowed_departments",
                    [],
                )

                allowed_roles = doc.get(
                    "allowed_roles",
                    [],
                )

                if not isinstance(
                    allowed_departments,
                    list,
                ):
                    allowed_departments = []

                if not isinstance(
                    allowed_roles,
                    list,
                ):
                    allowed_roles = []

                allowed_depts = [
                    str(d).upper()
                    for d in allowed_departments
                ]

                allowed_roles_upper = [
                    str(r).upper()
                    for r in allowed_roles
                ]

                # -----------------------------------------
                # ZERO-TRUST CLEARANCE CHECK
                # -----------------------------------------

                if user_rank < doc_rank:

                    blocked_docs.append({
                        "document_id": doc_id,
                        "reason": (
                            f"Clearance mismatch: "
                            f"requires {doc_class}, "
                            f"user has {user_clearance}"
                        ),
                    })

                    continue

                # -----------------------------------------
                # DEPARTMENT CHECK
                # -----------------------------------------

                dept_match = (
                    not allowed_depts
                    or user_dept in allowed_depts
                )

                # -----------------------------------------
                # ROLE CHECK
                # -----------------------------------------

                role_match = (
                    not allowed_roles_upper
                    or user_role in allowed_roles_upper
                )

                if dept_match and role_match:

                    authorized_docs.append(doc)

                else:

                    blocked_docs.append({
                        "document_id": doc_id,
                        "reason": (
                            "Role/Department mismatch: "
                            f"allowed_depts={allowed_depts}, "
                            f"allowed_roles={allowed_roles_upper}"
                        ),
                    })

            except Exception as ex:

                logger.warning(
                    f"Authorization error: {ex}"
                )

                document_id = (
                    doc.get("document_id", "ERROR_DOC")
                    if isinstance(doc, dict)
                    else "ERROR_DOC"
                )

                blocked_docs.append({
                    "document_id": document_id,
                    "reason": str(ex),
                })

        return authorized_docs, blocked_docs

    # =====================================================
    # DOCUMENT CONFLICT RESOLUTION
    # =====================================================

    def resolve_conflicts(
        self,
        docs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        if not docs:
            return []

        grouped: Dict[
            str,
            List[Dict[str, Any]]
        ] = {}

        for document in docs:

            title = str(
                document.get(
                    "title",
                    "",
                )
            ).strip().lower()

            grouped.setdefault(
                title,
                [],
            ).append(document)

        resolved: List[Dict[str, Any]] = []

        for title, cluster in grouped.items():

            if len(cluster) == 1:

                resolved.append(
                    cluster[0]
                )

                continue

            def sort_key(
                item: Dict[str, Any]
            ) -> Tuple[float, str]:

                try:

                    version = float(
                        str(
                            item.get(
                                "version",
                                "1.0",
                            )
                        ).replace(
                            "v",
                            "",
                        )
                    )

                except (ValueError, TypeError):

                    version = 1.0

                effective_date = str(
                    item.get(
                        "effective_date",
                        "1970-01-01",
                    )
                )

                return (
                    version,
                    effective_date,
                )

            cluster.sort(
                key=sort_key,
                reverse=True,
            )

            resolved.append(
                cluster[0]
            )

        return resolved

    # =====================================================
    # FINANCIAL PROCESSING
    # =====================================================

    def process_financial_prompt(
        self,
        user_id: str,
        prompt: str,
    ) -> Optional[Dict[str, Any]]:

        user_fin = self.user_financial_profiles.setdefault(
            user_id,
            {
                "monthly_budget": 10000.0,
                "expenses": {},
                "savings_goal": {
                    "name": "General",
                    "target": 20000.0,
                    "current": 5000.0,
                },
                "liquid_cash": 15000.0,
            },
        )

        clean_prompt = prompt.lower()

        # =================================================
        # EXPENSE LOGGING
        # =================================================

        spend_match = re.search(
            r"spent\s+(?:₹|rs\.?|inr)?\s*"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"(?:on|for)\s+"
            r"([a-zA-Z]+)",
            clean_prompt,
        )

        if spend_match:

            try:

                amount_text = (
                    spend_match
                    .group(1)
                    .replace(",", "")
                )

                amount = float(
                    amount_text
                )

                category = (
                    spend_match
                    .group(2)
                    .capitalize()
                )

                current_value = user_fin[
                    "expenses"
                ].get(
                    category,
                    0.0,
                )

                user_fin[
                    "expenses"
                ][category] = (
                    current_value + amount
                )

                user_fin[
                    "liquid_cash"
                ] = max(
                    0.0,
                    user_fin["liquid_cash"]
                    - amount,
                )

                total_spent = sum(
                    user_fin[
                        "expenses"
                    ].values()
                )

                budget = user_fin[
                    "monthly_budget"
                ]

                alert = None

                if total_spent > budget:

                    alert = (
                        "⚠️ BUDGET OVERRUN ALERT: "
                        f"Total spent ₹{total_spent:,.2f} "
                        f"exceeds limit ₹{budget:,.2f}!"
                    )

                return {
                    "action": "EXPENSE_LOGGED",
                    "category": category,
                    "amount": amount,
                    "updated_category_total": (
                        user_fin["expenses"][category]
                    ),
                    "total_monthly_expenses": total_spent,
                    "remaining_liquid_cash": (
                        user_fin["liquid_cash"]
                    ),
                    "alert": alert,
                }

            except Exception as e:

                raise FinancialLogicError(
                    f"Expense parsing failed: {e}"
                )

        # =================================================
        # BUDGET ANALYSIS
        # =================================================

        if (
            "budget" in clean_prompt
            and (
                "food" in clean_prompt
                or "spent" in clean_prompt
                or "adjust" in clean_prompt
            )
        ):

            # Try to extract user supplied numbers
            amounts = re.findall(
                r"(?:₹|rs\.?|inr)?\s*"
                r"([\d,]+(?:\.\d+)?)",
                clean_prompt,
            )

            parsed_amounts = []

            for value in amounts:

                try:

                    parsed_amounts.append(
                        float(
                            value.replace(
                                ",",
                                "",
                            )
                        )
                    )

                except ValueError:
                    pass

            # Profile defaults
            food_expense = user_fin[
                "expenses"
            ].get(
                "Food",
                12000.0,
            )

            budget = user_fin[
                "monthly_budget"
            ]

            # If prompt contains values such as
            # "spent ₹12,000 ... budget ₹8,000",
            # use those values.
            if len(parsed_amounts) >= 2:

                food_expense = parsed_amounts[0]
                budget = parsed_amounts[1]

            overrun = (
                food_expense - budget
            )

            pct_cut = (
                overrun
                / food_expense
                * 100
                if food_expense > 0
                else 0
            )

            if overrun > 0:

                recommendation = (
                    f"You have overspent your food budget "
                    f"by ₹{overrun:,.2f} "
                    f"({pct_cut:.1f}% above budget). "
                    "Action plan: "
                    "1) Cap discretionary spending; "
                    "2) Temporarily reduce dining out; "
                    "3) Reallocate available surplus "
                    "from non-essential categories."
                )

            else:

                recommendation = (
                    f"Your food spending is "
                    f"₹{abs(overrun):,.2f} "
                    "below the specified budget. "
                    "Continue monitoring spending "
                    "to stay within your target."
                )

            return {
                "action": "BUDGET_ADVICE",
                "food_expense": food_expense,
                "budget": budget,
                "deficit": overrun,
                "recommendation": recommendation,
            }

        # =================================================
        # FINANCIAL DECISION ANALYSIS
        # =================================================

        decision_keywords = [
            "should i buy",
            "should i invest",
            "should i book",
            "should i subscribe",
        ]

        if any(
            keyword in clean_prompt
            for keyword in decision_keywords
        ):

            # Find money values including ₹5,000
            amount_matches = re.findall(
                r"(?:₹|rs\.?|inr)?\s*"
                r"([\d,]+(?:\.\d+)?)",
                clean_prompt,
            )

            allocated_amount = 5000.0

            if amount_matches:

                try:

                    # Prefer the largest detected amount
                    # because prompts may contain several values.
                    numeric_values = [
                        float(
                            value.replace(
                                ",",
                                "",
                            )
                        )
                        for value in amount_matches
                    ]

                    allocated_amount = max(
                        numeric_values
                    )

                except ValueError:

                    allocated_amount = 5000.0

            liquid = user_fin.get(
                "liquid_cash",
                10000.0,
            )

            # ---------------------------------------------
            # LIQUIDITY SCORE
            # ---------------------------------------------

            if allocated_amount <= 0:

                liquidity_ratio = 1.0

            else:

                liquidity_ratio = min(
                    1.0,
                    liquid
                    / (
                        allocated_amount
                        * 2.5
                    ),
                )

            # ---------------------------------------------
            # GOAL SAFETY
            # ---------------------------------------------

            goal_safety_score = (
                0.85
                if liquid > allocated_amount
                else 0.35
            )

            # ---------------------------------------------
            # RISK
            # ---------------------------------------------

            high_risk_keywords = [
                "ipo",
                "crypto",
                "stock",
                "flight",
            ]

            is_high_risk = any(
                item in clean_prompt
                for item in high_risk_keywords
            )

            risk_penalty = (
                0.70
                if is_high_risk
                else 0.90
            )

            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            confidence_score = round(
                (
                    (
                        liquidity_ratio
                        * 0.4
                    )
                    + (
                        goal_safety_score
                        * 0.3
                    )
                    + (
                        risk_penalty
                        * 0.3
                    )
                )
                * 100,
                2,
            )

            decision = (
                "RECOMMENDED"
                if confidence_score >= 65
                else "NOT_RECOMMENDED"
            )

            # ---------------------------------------------
            # REASONING
            # ---------------------------------------------

            if (
                "flight" in clean_prompt
                or "goa" in clean_prompt
            ):

                reasoning = (
                    f"Liquid cash available is "
                    f"₹{liquid:,.2f}. "
                    f"The requested amount is "
                    f"₹{allocated_amount:,.2f}. "
                    "The system checks whether sufficient "
                    "liquidity remains for financial goals "
                    "and emergency reserves."
                )

            elif (
                "apple" in clean_prompt
                or "stock" in clean_prompt
            ):

                percentage = (
                    allocated_amount
                    / liquid
                    * 100
                    if liquid > 0
                    else 100
                )

                reasoning = (
                    f"Investing ₹{allocated_amount:,.2f} "
                    f"represents approximately "
                    f"{percentage:.1f}% of liquid reserves. "
                    "Equity investments carry market risk, "
                    "so available liquidity and financial "
                    "goals should be considered."
                )

            elif "ipo" in clean_prompt:

                reasoning = (
                    "IPO allocations carry uncertainty. "
                    "The system evaluates available liquidity, "
                    "allocation size, and risk before producing "
                    "a decision."
                )

            else:

                reasoning = (
                    f"Evaluated liquid balance "
                    f"₹{liquid:,.2f} against "
                    f"allocation ₹{allocated_amount:,.2f}."
                )

            return {
                "action": "DECISION_ANALYSIS",
                "verdict": decision,
                "confidence_score": (
                    f"{confidence_score}%"
                ),
                "allocation_amount": allocated_amount,
                "liquid_cash": liquid,
                "reasoning": reasoning,
            }

        return None

    # =====================================================
    # MAIN QUERY EXECUTION
    # =====================================================

    def execute_query(
        self,
        user: Dict[str, Any],
        prompt: str,
        documents: Optional[
            List[Dict[str, Any]]
        ] = None,
    ) -> Dict[str, Any]:

        timestamp = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        user_id = str(
            user.get(
                "user_id",
                "ANONYMOUS",
            )
        )

        clean_prompt = self.mask_pii(
            prompt.strip()
        )

        documents = documents or []

        audit_entry: Dict[str, Any] = {

            "timestamp": timestamp,

            "user_id": user_id,

            "prompt": clean_prompt,

            "authorized_docs": [],

            "blocked_docs": [],

            "status": "PROCESSING",
        }

        try:

            # ---------------------------------------------
            # FINANCIAL ANALYSIS
            # ---------------------------------------------

            fin_result = (
                self.process_financial_prompt(
                    user_id,
                    clean_prompt,
                )
            )

            # ---------------------------------------------
            # DOCUMENT AUTHORIZATION
            # ---------------------------------------------

            authorized_docs, blocked_docs = (
                self.authorize_documents(
                    user,
                    documents,
                )
            )

            audit_entry[
                "authorized_docs"
            ] = [
                d.get("document_id")
                for d in authorized_docs
            ]

            audit_entry[
                "blocked_docs"
            ] = blocked_docs

            # ---------------------------------------------
            # FINANCIAL ONLY QUERY
            # ---------------------------------------------

            if fin_result and not documents:

                audit_entry[
                    "status"
                ] = "SUCCESS_FINANCIAL"

                response = {

                    "status": "SUCCESS",

                    "type": "FINANCIAL_ADVISORY",

                    "details": fin_result,

                    "citations": [],
                }

            # ---------------------------------------------
            # NO DOCUMENT / NO FINANCIAL CONTEXT
            # ---------------------------------------------

            elif not documents:

                audit_entry[
                    "status"
                ] = "NO_CONTEXT"

                response = {

                    "status": "SAFE_REFUSAL",

                    "message": (
                        "No enterprise context "
                        "provided to answer the question."
                    ),

                    "citations": [],
                }

            # ---------------------------------------------
            # ACCESS DENIED
            # ---------------------------------------------

            elif not authorized_docs:

                audit_entry[
                    "status"
                ] = "ACCESS_DENIED"

                response = {

                    "status": "SAFE_REFUSAL",

                    "message": (
                        "Access Denied: You do not possess "
                        "the required clearance, role, or "
                        "departmental permissions to view "
                        "the documents relevant to this inquiry."
                    ),

                    "citations": [],
                }

            # ---------------------------------------------
            # AUTHORIZED DOCUMENTS
            # ---------------------------------------------

            else:

                resolved_docs = (
                    self.resolve_conflicts(
                        authorized_docs
                    )
                )

                citations = [

                    {
                        "document_id": d.get(
                            "document_id"
                        ),

                        "title": d.get(
                            "title"
                        ),

                        "version": d.get(
                            "version"
                        ),

                        "effective_date": d.get(
                            "effective_date"
                        ),

                        "classification": d.get(
                            "classification"
                        ),
                    }

                    for d in resolved_docs
                ]

                combined_content = " | ".join(
                    str(
                        d.get(
                            "content",
                            "",
                        )
                    )
                    for d in resolved_docs
                )

                audit_entry[
                    "status"
                ] = "SUCCESS_SYNTHESIS"

                response = {

                    "status": "SUCCESS",

                    "type": "DOCUMENT_SYNTHESIS",

                    "answer": (
                        "Based on authorized documents: "
                        + combined_content
                    ),

                    "citations": citations,
                }

                if fin_result:

                    response[
                        "supplementary_financial_analysis"
                    ] = fin_result

            # ---------------------------------------------
            # AUDIT LOG
            # ---------------------------------------------

            self.audit_log.append(
                audit_entry
            )

            return response

        except Exception as ex:

            logger.error(
                f"Execution failed: {ex}"
            )

            audit_entry[
                "status"
            ] = "FATAL_ERROR"

            audit_entry[
                "error"
            ] = str(ex)

            self.audit_log.append(
                audit_entry
            )

            return {

                "status": "ERROR",

                "message": (
                    "An unexpected system exception "
                    f"occurred: {str(ex)}"
                ),

                "citations": [],
            }


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="FinSecure AI",
    description=(
        "Unified Zero-Trust Enterprise "
        "Financial & Decision Agent"
    ),
    version="1.0.0",
)


# One agent instance for the running application
agent = FinSecureAgent()


# =========================================================
# REQUEST MODEL
# =========================================================

class QueryRequest(BaseModel):

    user: Dict[str, Any] = Field(
        ...,
        description="Authenticated user context",
    )

    prompt: str = Field(
        ...,
        min_length=1,
        description="User financial or enterprise query",
    )

    documents: Optional[
        List[Dict[str, Any]]
    ] = Field(
        default=None,
        description="Optional enterprise documents",
    )


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {

        "status": "online",

        "service": "FinSecure AI",

        "team": "Neural Nomads",

        "message": (
            "FinSecure AI is running successfully."
        ),
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "service": "FinSecure AI",
    }


# =========================================================
# QUERY ENDPOINT
# =========================================================

@app.post("/query")
def query(
    request: QueryRequest,
):

    try:

        return agent.execute_query(

            user=request.user,

            prompt=request.prompt,

            documents=request.documents,
        )

    except Exception as ex:

        logger.error(
            f"API query failed: {ex}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )


# =========================================================
# AUDIT LOG ENDPOINT
# =========================================================

@app.get("/audit")
def audit():

    return {

        "status": "SUCCESS",

        "entries": len(
            agent.audit_log
        ),

        "audit_log": agent.audit_log,
    }


# =========================================================
# LOCAL TESTING
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
