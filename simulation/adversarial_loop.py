def run_adversarial_simulation(case, service, fraudster, rounds=3):
    history = []

    for i in range(rounds):
        modified_case, tactics = fraudster.evade(case)
        report = service.investigate(modified_case)

        history.append({
            "round": i,
            "tactics": tactics,
            "decision": report["decision"],
            "confidence": report.get("confidence")
        })

        if report.get("decision") != "APPROVED":
            break

    return history