from backend.app.assistant import handle_message
from backend.app.store import STORE


def test_scenario_a_conversation_and_vivian_approve():
    STORE.reset()
    STORE.skip_fault_latency = True
    conv = {"id": "t", "actorId": "E10801", "messages": [], "pending": {"requesterId": "E10801"}}
    r1 = handle_message(
        conv,
        "I want to run Vitamin C effervescent at 89 in the 20 pilot stores for the next cycle.",
    )
    assert "WTC-VITC-1000-20" in r1["text"]
    r2 = handle_message(conv, "Correct")
    assert "forecast" in r2["text"].lower() or "need" in r2["text"].lower()
    r3 = handle_message(conv, "1,000 units, yes show the was-price, no funding — it's own brand.")
    assert "38.20%" in r3["text"] or "38.2%" in r3["text"]
    assert "Band A" in r3["text"]
    assert "Vivian Chan" in r3["text"]
    r4 = handle_message(conv, "Yes")
    assert "PR-2026-1042" in r4["text"]
    case = STORE.cases["PR-2026-1042"]
    assert case["status"] == "AWAITING_APPROVAL"
    from backend.app.cases import decide_task

    tid = case["tasks"][0]
    decide_task(tid, "APPROVE", "E10234")
    assert STORE.cases["PR-2026-1042"]["draftId"] == "PD-2026-1042"


def test_knowledge_and_blocked_formula():
    STORE.reset()
    conv = {"id": "t", "actorId": "E10822", "messages": [], "pending": {"requesterId": "E10822"}}
    r = handle_message(conv, "Can I run a flash on MediRelief ibuprofen this weekend?")
    assert "PHARMACY_ONLY_P1" in r["text"]
    r2 = handle_message(conv, "Can we do 10% off PureNest Stage 1 for members in C22?")
    assert "BLOCKED" in r2["text"] or "cannot be promoted" in r2["text"]
    assert r2["cards"]["case"]["status"] == "BLOCKED_REGULATORY"
