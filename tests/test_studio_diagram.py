from backend.app.store import STORE
from backend.app.studio import compose_diagram, studio_state, workflow_blueprint


def _version(tag: str) -> dict:
    bp = workflow_blueprint()
    return next(v for v in bp["versions"] if v["version"] == tag)


def test_draft_diagram_is_sequence_flow_not_a_list():
    diagram = compose_diagram(_version("0.1"))
    ids = {n["id"] for n in diagram["nodes"]}
    kinds = {n["id"]: n["kind"] for n in diagram["nodes"]}
    flows = {(f["source"], f["target"], f["label"]) for f in diagram["sequenceFlows"]}

    assert diagram["notation"] == "BPMN sequence flow"
    assert diagram["counts"]["activities"] == 12
    assert "start" in ids and kinds["start"] == "startEvent"
    assert "end" in ids and kinds["end"] == "endEvent"
    assert kinds["S03__xor"] == "exclusiveGateway"
    assert kinds["S03__blocked"] == "endEvent"
    assert ("S03", "S03__xor", "") in flows
    assert ("S03__xor", "S03__blocked", "BLOCKED") in flows
    assert ("S03__xor", "S04", "proceed") in flows
    assert ("start", "S01", "") in flows
    assert ("S12", "end", "") in flows
    # no stacked-list leftover: every activity sits on a sequence flow
    activity_ids = [n["id"] for n in diagram["nodes"] if n["kind"] == "activity"]
    touched = {f["source"] for f in diagram["sequenceFlows"]} | {f["target"] for f in diagram["sequenceFlows"]}
    assert set(activity_ids) <= touched


def test_approved_diagram_has_upload_loop_and_parallel_humans():
    diagram = compose_diagram(_version("1.0"))
    kinds = {n["id"]: n["kind"] for n in diagram["nodes"]}
    labels = {n["id"]: n["label"] for n in diagram["nodes"]}
    flows = {(f["source"], f["target"], f["label"]) for f in diagram["sequenceFlows"]}

    assert diagram["counts"]["activities"] == 14
    assert kinds["S05__human"] == "userTask"
    assert "upload" in labels["S05__human"].lower() or "letter" in labels["S05__human"].lower()
    assert ("S05", "S05__human", "evidence needed") in flows
    assert kinds["S12__and"] == "parallelGateway"
    assert kinds["S12__decision"] == "exclusiveGateway"
    assert any(t == "S13" and lbl == "approved" for _, t, lbl in flows)
    assert any(lbl == "returned / rejected" for _, _, lbl in flows)
    assert any(n["kind"] == "userTask" and "Finance" in n["label"] for n in diagram["nodes"])
    assert any(n["kind"] == "userTask" and "Approver" in n["label"] for n in diagram["nodes"])
    assert any(n["kind"] == "userTask" and "Compliance" in n["label"] for n in diagram["nodes"])
    assert all(f["source"] != f["target"] for f in diagram["sequenceFlows"])


def test_studio_state_exposes_generated_diagram():
    STORE.reset()
    state = studio_state()
    assert state["diagram"]["version"] == "0.1"
    assert state["diagram"]["counts"]["sequenceFlows"] >= 12
    assert state["diagram"]["nodes"][0]["kind"] == "startEvent"
