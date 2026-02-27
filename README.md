# Xyper-AI : A Governed Agentic AI Framework for Interpretable and Safe Fraud Investigation

This repository contains the implementation artifacts, system design, and research materials associated with the paper:

> **A Governed Agentic AI Framework for Interpretable and Safe Fraud Investigation**  
> *Journal: International Journal of Data Science and Analytics (Under Consideration)*

The work presents a **governed agentic AI system** for fraud investigation that prioritizes **interpretability, safety, and human oversight** over black-box automation.

---

## Motivation

Financial fraud investigation is a **high-stakes, regulated decision-making problem**.  
While modern ML models achieve high accuracy, they often lack:

- Explainability  
- Confidence calibration  
- Explicit safety and governance controls  

This project addresses these gaps by designing an **agent-based investigation system** with **bounded execution, critic-based decision governance, and human-in-the-loop escalation**.

---

## Core Idea

Instead of directly predicting fraud labels, the system performs an **explicit investigation process**, similar to how human analysts operate.

Key principles:
- Evidence-driven reasoning
- Confidence-aware decisions
- Policy-compliant automation
- Safe escalation to human reviewers

---

## System Architecture

The system is composed of multiple specialized agents orchestrated via a governed execution graph:

- **Planner Agent** – generates investigation plans under constraints  
- **Transaction Agent** – detects transaction-level anomalies  
- **User Behavior Agent** – analyzes deviations from historical patterns  
- **Risk Agent** – evaluates contextual and geographic risk  
- **Critic Agent** – aggregates evidence, calibrates confidence, and governs decisions  
- **Policy Engine** – enforces safety and compliance rules  
- **Human Review Gate** – escalates low-confidence or policy-violating cases  

The architecture ensures **termination guarantees, auditability, and regulatory alignment**.

---

## Decision Governance & Safety

A dedicated governance layer ensures:
- Bounded reasoning steps
- Explicit confidence thresholds
- No automated approval under uncertainty
- Human oversight when required

This design aligns with principles of **Explainable AI (XAI)** and **responsible AI deployment** in regulated environments.

---

## Experimental Setup

- **Dataset**: PaySim (synthetic mobile money transaction dataset)
- **Evaluation Focus**:
  - Decision outcomes (automation vs. escalation)
  - Confidence calibration
  - Escalation behavior

The goal is **decision safety and interpretability**, not raw classification accuracy.

---

## Paper Status

**Journal: International Journal of Data Science and Analytics (Under Consideration)**
Status: Under editorial processing

> This repository will be updated with revisions and camera-ready versions as the review process progresses.

---

## Authors

- Harsh Satishkumar Patel
- MSc Data Science, Dhirubhai Ambani University (DAU), India
- harshpatel080503@gmail.com

- Urvi Jitendrabhai Kava
- MSc Data Science, Dhirubhai Ambani University (DAU), India
- urvikawa2004@gmail.com

---

## License

This project is released under the MIT License.
See the LICENSE file for details.

---

## Citation

If you find this work useful, please consider citing the paper (once published):
```bibtex
@article{xyper2026agentic,
  title={A Governed Agentic AI Framework for Interpretable and Safe Fraud Investigation},
  author={Patel, Harsh Satishkumar and Kava, Urvi Jitendrabhai},
  journal={SN Computer Science},
  year={2026}
}
```

---

## Future Work

Planned extensions include:

- Controlled online learning from analyst feedback

- Formal verification of policy constraints

- Adversarial fraud simulation

- Extension to compliance and audit automation workflows

---

## Contributions

Issues, discussions, and constructive feedback are welcome.
Please open an issue or reach out via email.
