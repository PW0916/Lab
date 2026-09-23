"""FastAPI entry — mock systems + Workflow Studio + Workflow Assistant."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import assistant, cases, studio
from .dates import parse_date
from .engine import evaluate_request
from .mocks import router as mock_router
from .store import ROOT, STORE

app = FastAPI(
    title="WTCHK Promotion Approval Citizen Demo",
    version="2.0.0",
    description="Workflow Studio + Workflow Assistant on a simulated nine-system layer.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(mock_router, prefix="/asw-wtchk")
app.include_router(mock_router, prefix="/api/mocks")


def _conversation(actor_id: str | None = None) -> dict:
    aid = actor_id or STORE.identity_id
    cid = f"conv-{aid}"
    if cid not in STORE.conversations:
        STORE.conversations[cid] = {
            "id": cid,
            "actorId": aid,
            "messages": [],
            "pending": {"requesterId": aid},
            "language": "en",
        }
    conv = STORE.conversations[cid]
    conv["actorId"] = aid
    return conv


@app.get("/api/health")
def health():
    return {"ok": True, "clock": STORE.clock.isoformat(), "identity": STORE.identity_id}


@app.get("/api/demo/state")
def demo_state():
    return {
        "clock": STORE.clock.isoformat(),
        "fault": STORE.fault,
        "identity": STORE.identity(),
        "people": STORE.people(),
        "labels": STORE.studio["labels"],
        "studio": STORE.studio,
        "caseCount": len(STORE.cases),
        "taskCount": len(STORE.tasks),
    }


@app.post("/api/demo/reset")
def demo_reset(body: dict | None = None):
    STORE.reset()
    if (body or {}).get("seed"):
        from .seed import seed_storyline

        seed_storyline()
    return demo_state()


@app.post("/__demo/reset")
def demo_reset_alias():
    STORE.reset()
    return {"ok": True}


@app.get("/__demo/state")
def demo_inspect():
    return {
        "cases": list(STORE.cases.keys()),
        "tasks": list(STORE.tasks.keys()),
        "drafts": list(STORE.drafts.keys()),
        "clock": STORE.clock.isoformat(),
        "counters": STORE.counters,
    }


@app.post("/api/demo/clock")
def set_clock(body: dict):
    STORE.clock = parse_date(body.get("clock") or body.get("date"))
    cases.refresh_all_tasks()
    return demo_state()


@app.post("/api/demo/fault")
def set_fault(body: dict):
    STORE.fault = body.get("fault") or None
    return demo_state()


@app.post("/api/demo/identity")
def set_identity(body: dict):
    STORE.identity_id = body["employeeId"]
    return demo_state()


@app.get("/api/studio")
def get_studio():
    return studio.studio_state()


@app.get("/api/studio/documents/{file_name}")
def get_document(file_name: str):
    return {"file": file_name, "text": studio.document_text(file_name)}


@app.get("/api/studio/findings/{finding_id}")
def get_finding(finding_id: str):
    km = studio.knowledge_model()
    row = next((f for f in km.get("findings") or [] if f["id"] == finding_id), None)
    if not row:
        return {"error": "not found"}
    return row


@app.post("/api/studio/feedback")
def post_feedback(body: dict):
    return studio.apply_feedback(int(body["item"]), send_change_request=bool(body.get("send")))


@app.post("/api/studio/approve")
def post_approve(body: dict | None = None):
    return studio.approve_blueprint((body or {}).get("by") or "Mei Wong")


@app.post("/api/assistant/message")
def post_message(body: dict):
    conv = _conversation(body.get("actorId") or STORE.identity_id)
    text = body.get("text") or ""
    conv["messages"].append({"role": "user", "text": text})
    reply = assistant.handle_message(conv, text, body.get("upload"))
    conv["messages"].append({"role": "assistant", "text": reply["text"], "cards": reply.get("cards")})
    return {"reply": reply, "conversation": conv, "identity": STORE.identity()}


@app.post("/api/assistant/upload")
async def post_upload(file: UploadFile = File(...), actorId: str | None = Form(default=None)):
    conv = _conversation(actorId or STORE.identity_id)
    raw = await file.read()
    name = file.filename or "upload.md"
    conv["messages"].append({"role": "user", "text": f"[uploaded {name}]", "upload": name})
    reply = assistant.handle_message(conv, f"I have the letter {name}", {"filename": name, "bytes": len(raw)})
    conv["messages"].append({"role": "assistant", "text": reply["text"], "cards": reply.get("cards")})
    return {"reply": reply, "conversation": conv}


@app.get("/api/cases")
def list_cases():
    cases.refresh_all_tasks()
    return {"cases": cases.cases_for(STORE.identity_id), "all": [cases._public_case(c) for c in STORE.cases.values()]}


@app.get("/api/cases/{case_ref}")
def get_case(case_ref: str):
    cases.refresh_all_tasks()
    return cases._public_case(STORE.cases.get(case_ref))


@app.post("/api/evaluate")
def post_evaluate(body: dict):
    """Direct evaluation for tests and the Studio scenario runner."""
    return evaluate_request(STORE, body)


@app.get("/api/inbox")
def get_inbox(employeeId: str | None = None):
    return {"inbox": cases.inbox_for(employeeId or STORE.identity_id)}


@app.post("/api/inbox/{task_id}/decide")
def decide(task_id: str, body: dict):
    task = cases.decide_task(
        task_id,
        body["decision"],
        body.get("decidedBy") or STORE.identity_id,
        conditions=body.get("conditions"),
        comment=body.get("comment"),
        delegationRef=body.get("delegationRef"),
    )
    case = STORE.cases.get(task.get("caseRef"))
    return {"task": task, "case": cases._public_case(case)}


@app.get("/api/knowledge")
def knowledge_q(q: str):
    answer = assistant.knowledge_answer(q)
    return {"question": q, "answer": answer}


DIST = ROOT / "frontend" / "dist"
if DIST.exists():
    assets = DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        candidate = DIST / full_path
        if full_path and candidate.exists() and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
