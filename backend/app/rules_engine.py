"""
Rules Engine for Antiarrhythmic Medication Safety
Works only with synthetic profiles.
"""

from datetime import date, timedelta
from typing import List, Dict, Any
from .schemas import Alert


def assess_patient(patient: Any) -> Dict[str, Any]:
    """
    Main entry point.
    Returns dict with overall_risk, alerts list, and recommendations.
    """
    alerts: List[Alert] = []

    drug = (patient.antiarrhythmic_drug or "").strip().lower()

    # ---------- Common checks ----------
    alerts.extend(_check_electrolytes(patient))
    alerts.extend(_check_renal(patient))
    alerts.extend(_check_overdue_monitoring(patient))

    # ---------- Drug-specific rules ----------
    if "sotalol" in drug:
        alerts.extend(_sotalol_rules(patient))
    elif "flecainide" in drug:
        alerts.extend(_flecainide_rules(patient))
    elif "amiodarone" in drug:
        alerts.extend(_amiodarone_rules(patient))
    elif "dronedarone" in drug:
        alerts.extend(_dronedarone_rules(patient))

    # ---------- Combination / rate-limiting ----------
    alerts.extend(_rate_limiting_combinations(patient))

    # Determine overall risk
    overall_risk = _calculate_overall_risk(alerts)
    recommendations = list({a.recommendation for a in alerts if a.recommendation})

    return {
        "overall_risk": overall_risk,
        "alerts": alerts,
        "recommendations": recommendations
    }


# ==================== Helper functions ====================

def _check_electrolytes(p) -> List[Alert]:
    alerts = []
    if p.potassium is not None:
        if p.potassium < 3.5:
            alerts.append(Alert(
                severity="high" if p.potassium < 3.0 else "warning",
                code="LOW_K",
                message=f"Low potassium ({p.potassium} mmol/L)",
                recommendation="Correct hypokalaemia before continuing QT-prolonging antiarrhythmics. Recheck electrolytes."
            ))
        elif p.potassium > 5.5:
            alerts.append(Alert(
                severity="warning",
                code="HIGH_K",
                message=f"High potassium ({p.potassium} mmol/L)",
                recommendation="Investigate and manage hyperkalaemia."
            ))

    if p.magnesium is not None and p.magnesium < 0.7:
        alerts.append(Alert(
            severity="warning",
            code="LOW_MG",
            message=f"Low magnesium ({p.magnesium} mmol/L)",
            recommendation="Correct hypomagnesaemia, especially if on QT-prolonging drugs."
        ))
    return alerts


def _check_renal(p) -> List[Alert]:
    alerts = []
    if p.egfr is not None and p.egfr < 60:
        severity = "high" if p.egfr < 30 else "warning"
        alerts.append(Alert(
            severity=severity,
            code="IMPAIRED_RENAL",
            message=f"Reduced eGFR ({p.egfr} mL/min/1.73m²)",
            recommendation="Review dose of renally cleared drugs (especially Sotalol). Consider dose reduction or alternative."
        ))
    return alerts


def _check_overdue_monitoring(p) -> List[Alert]:
    alerts = []
    today = date.today()

    def overdue(last_date, months, name):
        if last_date is None:
            return Alert(
                severity="warning",
                code=f"MISSING_{name.upper()}",
                message=f"No recorded {name} date",
                recommendation=f"Perform baseline {name} and document the date."
            )
        if (today - last_date).days > months * 30:
            return Alert(
                severity="warning",
                code=f"OVERDUE_{name.upper()}",
                message=f"{name} overdue (last: {last_date})",
                recommendation=f"Schedule {name} as soon as possible."
            )
        return None

    # Amiodarone needs more frequent thyroid & LFT
    drug = (p.antiarrhythmic_drug or "").lower()
    thyroid_months = 6 if "amiodarone" in drug else 12
    lft_months = 6 if "amiodarone" in drug else 12

    for check in [
        overdue(p.last_thyroid_date, thyroid_months, "Thyroid function"),
        overdue(p.last_lft_date, lft_months, "Liver function tests"),
        overdue(p.last_electrolytes_date, 6, "Electrolytes"),
        overdue(p.last_ecg_date, 6, "ECG"),
        overdue(p.last_renal_date, 6, "Renal function"),
    ]:
        if check:
            alerts.append(check)
    return alerts


def _sotalol_rules(p) -> List[Alert]:
    alerts = []

    if p.qtc is not None and p.qtc > 480:
        severity = "critical" if p.qtc > 500 else "high"
        alerts.append(Alert(
            severity=severity,
            code="SOTALOL_LONG_QTC",
            message=f"Sotalol + prolonged QTc ({p.qtc} ms)",
            recommendation="Stop or reduce Sotalol. Continuous ECG monitoring. Correct electrolytes. Consider alternative agent."
        ))

    if p.potassium is not None and p.potassium < 4.0:
        alerts.append(Alert(
            severity="high",
            code="SOTALOL_LOW_K",
            message=f"Sotalol + low/borderline potassium ({p.potassium} mmol/L)",
            recommendation="Maintain K+ ≥ 4.0 mmol/L while on Sotalol. Supplement if needed."
        ))

    if p.egfr is not None and p.egfr < 60:
        alerts.append(Alert(
            severity="high",
            code="SOTALOL_RENAL",
            message=f"Sotalol + impaired renal function (eGFR {p.egfr})",
            recommendation="Sotalol is renally cleared. Reduce dose or avoid if eGFR < 40. Close QT monitoring."
        ))

    if p.heart_rate is not None and p.heart_rate < 50:
        alerts.append(Alert(
            severity="warning",
            code="SOTALOL_BRADY",
            message=f"Bradycardia on Sotalol (HR {p.heart_rate})",
            recommendation="Review dose. Consider temporary holding if symptomatic."
        ))

    return alerts


def _flecainide_rules(p) -> List[Alert]:
    alerts = []

    # Structural heart disease / low LVEF
    if p.lvef is not None and p.lvef < 40:
        alerts.append(Alert(
            severity="critical",
            code="FLECAINIDE_LOW_LVEF",
            message=f"Flecainide + reduced LVEF ({p.lvef}%)",
            recommendation="Flecainide is contraindicated in structural heart disease / significant LV impairment. Stop drug and choose alternative."
        ))
    elif p.lvef is not None and p.lvef < 50:
        alerts.append(Alert(
            severity="high",
            code="FLECAINIDE_BORDERLINE_LVEF",
            message=f"Flecainide + borderline LVEF ({p.lvef}%)",
            recommendation="Use with extreme caution. Prefer alternative agents if any structural disease present."
        ))

    if p.qrs_duration is not None and p.qrs_duration > 150:
        alerts.append(Alert(
            severity="high",
            code="FLECAINIDE_WIDE_QRS",
            message=f"Flecainide + wide QRS ({p.qrs_duration} ms)",
            recommendation="QRS widening > 25% from baseline or absolute > 150 ms is an indication to stop or reduce Flecainide."
        ))
    elif p.qrs_duration is not None and p.qrs_duration > 120:
        alerts.append(Alert(
            severity="warning",
            code="FLECAINIDE_QRS_WIDENING",
            message=f"Flecainide + QRS {p.qrs_duration} ms",
            recommendation="Monitor QRS closely. Increase is a warning sign of toxicity."
        ))

    return alerts


def _amiodarone_rules(p) -> List[Alert]:
    alerts = []

    if p.heart_rate is not None and p.heart_rate < 50:
        alerts.append(Alert(
            severity="warning",
            code="AMIO_BRADY",
            message=f"Bradycardia on Amiodarone (HR {p.heart_rate})",
            recommendation="Review dose and concurrent rate-limiting drugs."
        ))

    if p.tsh is not None:
        if p.tsh > 5.0:
            alerts.append(Alert(
                severity="high",
                code="AMIO_HYPO_THYROID",
                message=f"Raised TSH on Amiodarone ({p.tsh})",
                recommendation="Evaluate for amiodarone-induced hypothyroidism. Consider endocrinology input."
            ))
        elif p.tsh < 0.3:
            alerts.append(Alert(
                severity="high",
                code="AMIO_HYPER_THYROID",
                message=f"Suppressed TSH on Amiodarone ({p.tsh})",
                recommendation="Evaluate for amiodarone-induced thyrotoxicosis (Type 1 or 2)."
            ))

    if p.alt is not None and p.alt > 100:
        alerts.append(Alert(
            severity="high",
            code="AMIO_HIGH_ALT",
            message=f"Elevated ALT on Amiodarone ({p.alt} U/L)",
            recommendation="Monitor LFTs closely. Consider dose reduction or alternative if persistent rise."
        ))

    return alerts


def _dronedarone_rules(p) -> List[Alert]:
    alerts = []
    if p.lvef is not None and p.lvef < 40:
        alerts.append(Alert(
            severity="critical",
            code="DRONEDARONE_HF",
            message="Dronedarone + heart failure / low LVEF",
            recommendation="Dronedarone is contraindicated in permanent AF with heart failure or recent decompensation."
        ))
    return alerts


def _rate_limiting_combinations(p) -> List[Alert]:
    """Simple check for multiple rate-limiting agents."""
    alerts = []
    other = (p.other_medications or "").lower()
    drug = (p.antiarrhythmic_drug or "").lower()

    rate_limiters = []
    if any(x in drug for x in ["sotalol", "amiodarone"]):
        rate_limiters.append(drug)
    if "bisoprolol" in other or "nebivolol" in other or "atenolol" in other or "metoprolol" in other or "carvedilol" in other:
        rate_limiters.append("beta-blocker")
    if "verapamil" in other or "diltiazem" in other:
        rate_limiters.append("non-DHP CCB")
    if "digoxin" in other:
        rate_limiters.append("digoxin")

    if len(rate_limiters) >= 2:
        alerts.append(Alert(
            severity="high",
            code="MULTI_RATE_LIMIT",
            message=f"Multiple rate-limiting agents: {', '.join(rate_limiters)}",
            recommendation="High risk of significant bradycardia or heart block. Review necessity of each agent and monitor HR closely."
        ))
    return alerts


def _calculate_overall_risk(alerts: List[Alert]) -> str:
    if not alerts:
        return "low"
    severities = {a.severity for a in alerts}
    if "critical" in severities:
        return "critical"
    if "high" in severities:
        return "high"
    if "warning" in severities:
        return "moderate"
    return "low"
