#!/usr/bin/env python3
"""Export database agent skills research to Word document."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_cell_shading(cell, fill: str) -> None:
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shading)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], header_fill: str = "D9E2F3") -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, text in enumerate(headers):
        hdr[i].text = text
        set_cell_shading(hdr[i], header_fill)
        for p in hdr[i].paragraphs:
            for run in p.runs:
                run.bold = True
    for row in rows:
        cells = table.add_row().cells
        for i, text in enumerate(row):
            cells[i].text = text
    doc.add_paragraph()


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_code_block(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)


def build_document() -> Document:
    doc = Document()

    title = doc.add_heading("AI Agent Skills for Database Research & Continuous Self-Improvement", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run("Research Report — July 3, 2026")
    run.italic = True
    run.font.color.rgb = RGBColor(89, 89, 89)

    doc.add_paragraph(
        "This report summarizes the most relevant agent skills and architectural patterns for "
        "enabling AI agents to study databases, accumulate knowledge across sessions, and "
        "continuously improve query and schema understanding over time."
    )

    # Section 1
    doc.add_heading("1. The Key Insight", level=1)
    doc.add_paragraph(
        "Most database skills (e.g. supabase-postgres-best-practices, 264K installs) are static "
        "playbooks. They teach SQL best practices but do not learn your schema or improve from "
        "past queries by themselves."
    )
    doc.add_paragraph(
        "Continuous database learning requires three layers working together:"
    )
    add_table(
        doc,
        ["Layer", "Role", "Example"],
        [
            ["Study", "Explore schema, run queries, document findings", "motherduck-explore, Chion compile"],
            ["Memory", "Persist schema notes, join patterns, past errors", "madb-memory, deep-agents-memory, schema_notes.md"],
            ["Evolution", "Turn successes/failures into updated skills", "self-improving-agent, continuous-learning-v2, GEPA SQL agent"],
        ],
    )
    doc.add_paragraph(
        "No single skill does all three well today. The best setups combine a database skill + "
        "a memory skill + a self-improvement skill."
    )

    # Section 2
    doc.add_heading("2. Tier 1: Best Skills for Continuous Database Learning", level=1)

    tier1 = [
        (
            "2.1 self-improving-agent — 31.5K installs",
            "Source: charon-fan/agent-playbook",
            "Install: npx skills add charon-fan/agent-playbook --skill self-improving-agent --agent cursor -y",
            [
                "Universal self-improvement system that learns from every skill run",
                "Semantic memory — abstract patterns/rules (memory/semantic-patterns.json)",
                "Episodic memory — specific sessions (memory/episodic/)",
                "Hooks — auto-triggers on skill complete/error",
                "Promotion policy — validated patterns get written back into SKILL.md",
            ],
            "Pair with a database skill. After a query fails or the user corrects a join, it can "
            "capture patterns like 'orders.user_id joins users.id, not customer_id' and promote "
            "them into your DB skill over time.",
        ),
        (
            "2.2 continuous-learning-v2 — 7.3K installs",
            "Source: affaan-m/everything-claude-code",
            "Install: npx skills add affaan-m/everything-claude-code --skill continuous-learning-v2 --agent cursor -y",
            [
                "Instinct-based learning via hooks (100% tool-call capture)",
                "Creates atomic instincts with confidence scores (0.3–0.9)",
                "/evolve clusters instincts into new skills/commands",
                "Project-scoped — SQL patterns stay in DB project, not global",
            ],
            "Instincts like 'always check null rates before aggregating revenue' can evolve into "
            "a project-specific database skill.",
        ),
        (
            "2.3 madb-memory — causal memory + skill capture",
            "Source: spshkar84/madb-meta-agents-db (requires MADB MCP server)",
            "",
            [
                "recall — pull prior schema decisions before querying",
                "remember — store decisions with caused_by lineage",
                "save_skill — turn repeatable DB workflows into reusable procedures",
                "trace_cause — explain why a query approach was chosen",
            ],
            "Best for 'why did we join these tables this way?' and building causal history of "
            "schema discoveries across sessions.",
        ),
        (
            "2.4 knowledge-ops — 3.5K installs",
            "Source: affaan-m/everything-claude-code",
            "",
            [
                "Multi-layer knowledge system (6 layers)",
                "Layer 2: Claude/Cursor project memory files",
                "Layer 3: MCP knowledge graph (entities, relations, observations)",
                "Layer 5: PostgreSQL/Supabase for large structured knowledge",
                "Ingestion, dedup, sync across sources",
            ],
            "Good for storing schema_notes.md, query_patterns.md, and glossary.md — the same "
            "pattern used in production self-learning SQL agents.",
        ),
        (
            "2.5 deep-agents-memory — 11.5K installs",
            "Source: langchain-ai/langchain-skills",
            "Install: npx skills add langchain-ai/langchain-skills --skill deep-agents-memory --agent cursor -y",
            [
                "StateBackend — ephemeral (single thread)",
                "StoreBackend — persists across sessions (PostgresStore in prod)",
                "CompositeBackend — route paths (/schema/ persistent, /tmp/ ephemeral)",
            ],
            "Store schema maps and query playbooks in persistent paths while keeping scratch work ephemeral.",
        ),
        (
            "2.6 Chion — schema-grounded, auto-updating SQL skills",
            "Source: chion.ai (not on skills.sh; compiles to SKILL.md)",
            "",
            [
                "Connects read-only to Postgres, profiles schema",
                "Compiles verified queries into portable SKILL.md + scripts/query.sql",
                "Re-compiles when schema changes",
                "Every line cited back to a verified query",
            ],
            "Closest to 'agent studies DB and knowledge compounds' in product form. "
            "Learning is query-verified, not free-form notes.",
        ),
    ]

    for title_text, source, install, bullets, why in tier1:
        doc.add_heading(title_text, level=2)
        doc.add_paragraph(source)
        if install:
            add_code_block(doc, install)
        doc.add_paragraph("What it does:")
        add_bullets(doc, bullets)
        p = doc.add_paragraph()
        r = p.add_run("Why it fits DB research: ")
        r.bold = True
        p.add_run(why)

    # Section 3
    doc.add_heading("3. Tier 2: Database Skills with Learning-Friendly Design", level=1)
    add_table(
        doc,
        ["Skill", "Installs", "Continuous-learning angle"],
        [
            ["motherduck-explore", "~200", "Structured exploration workflow; output feeds memory"],
            ["motherduck-query", "~200", "Query playbook; pair with self-improving-agent"],
            ["duckdb-skills@read-memories", "346", "Searches past agent sessions for prior DB decisions"],
            ["duckdb-skills@query", "612", "Session state in .duckdb-skills/state.sql persists schema context"],
            ["supabase-postgres-best-practices", "264K", "Rich references; good base skill to evolve via promotion"],
            ["text-to-sql (oimiragieo)", "132", "Dedicated NL→SQL; low adoption"],
            ["agentdb-memory-patterns (ruvnet/ruflo)", "863", "Reflexion replay, skill library, episodic consolidation"],
        ],
    )

    # Section 4
    doc.add_heading("4. Tier 3: Research Projects (Architectural Patterns)", level=1)
    doc.add_paragraph(
        "These GitHub projects are not installable skills but define how continuous DB learning "
        "is built in practice:"
    )
    add_table(
        doc,
        ["Project", "Learning mechanism", "Persistent artifacts"],
        [
            ["gepa-tuned-sql-agent", "User feedback → prompt evolution (GEPA) + RL bandit", "connections.json, rl-weights.json"],
            ["CortexKG", "Error lessons + pgvector few-shot memory", "kg_error_summary, semantic query memory"],
            ["QueryMind", "Multi-layer memory (schema separate from conversation)", "Business metadata graph"],
            ["Self-Improving-Text2SQL", "ACE: Generator → Reflector → Curator", "playbook.json, episodic_memory.jsonl"],
            ["AgentDB", "Demand-constructed context from SQLite tiers + skill graph", "skills, skill_implementations tables"],
            ["Claude Managed SQL Agent", "Coordinator-owned memory files", "glossary.md, schema_notes.md, query_patterns.md"],
        ],
    )
    doc.add_paragraph("Shared pattern across all projects:")
    add_code_block(
        doc,
        "Explore schema → Query → Validate → Extract lesson → Update playbook/skill → Recall next time",
    )

    # Section 5
    doc.add_heading("5. How Continuous DB Learning Works", level=1)
    doc.add_paragraph("Architecture flow:")
    add_bullets(
        doc,
        [
            "Session 1: Explore schema → Write SQL → Execute/validate → Extract lesson",
            "Lessons stored in: schema_notes.md, query_patterns.md, glossary.md, episodic traces",
            "Evolution loop: User feedback + episodic traces → self-improving-agent / continuous-learning-v2",
            "Validated patterns promoted into updated SKILL.md",
            "Session 2: Recall memory → Better query on first try",
        ],
    )

    # Section 6
    doc.add_heading("6. Recommended Stacks by Goal", level=1)

    doc.add_heading("6.1 Agent learns my Postgres schema over time", level=2)
    add_code_block(
        doc,
        "# Study + query\n"
        "npx skills add supabase/agent-skills --skill supabase-postgres-best-practices --agent cursor -y\n\n"
        "# Memory\n"
        "npx skills add langchain-ai/langchain-skills --skill deep-agents-memory --agent cursor -y\n\n"
        "# Evolution\n"
        "npx skills add charon-fan/agent-playbook --skill self-improving-agent --agent cursor -y\n"
        "npx skills add affaan-m/everything-claude-code --skill continuous-learning-v2 --agent cursor -y",
    )
    doc.add_paragraph("Also maintain project files: schema_notes.md, query_patterns.md, glossary.md")

    stacks = [
        ("6.2 Verified SQL that stays grounded as schema changes", "Chion (chion.ai/sql-skills-generator) — auto-compiles live schema + verified queries into SKILL.md"),
        ("6.3 Agent remembers why past query decisions were made", "madb-memory + MADB MCP server (save_skill, trace_cause)"),
        ("6.4 Self-improving Text-to-SQL from user corrections", "Study gepa-tuned-sql-agent or Self-Improving-Text2SQL (ACE playbook pattern)"),
        ("6.5 Local file/data research with session memory", "duckdb/duckdb-skills + self-improving-agent"),
    ]
    for heading, desc in stacks:
        doc.add_heading(heading, level=2)
        doc.add_paragraph(desc)

    # Section 7
    doc.add_heading("7. What to Avoid", level=1)
    add_table(
        doc,
        ["Skill", "Why it's misleading"],
        [
            ["dbs-learning (6.3K installs)", "Interactive topic learning for a business brand — NOT database learning"],
            ["supabase-postgres-best-practices alone", "Excellent reference, but static — no memory or evolution"],
            ["text-to-sql skills (~132 installs)", "Very low adoption; no built-in continuous learning"],
            ["Community auto-generated skills", "Often stale; prefer vendor-maintained + explicit memory layer"],
        ],
    )

    # Section 8
    doc.add_heading("8. Bottom Line", level=1)
    doc.add_paragraph(
        "There is no single popular skill that fully 'studies a database and keeps improving itself' "
        "out of the box. The ecosystem splits into:"
    )
    add_table(
        doc,
        ["Need", "Best option"],
        [
            ["Study DB", "motherduck-explore, supabase-postgres-best-practices, Chion"],
            ["Remember across sessions", "madb-memory, deep-agents-memory, knowledge-ops, project schema_notes.md"],
            ["Improve over time", "self-improving-agent (31.5K), continuous-learning-v2 (7.3K)"],
            ["Schema-grounded, auto-refreshing skills", "Chion (compiles from live Postgres)"],
            ["Research-grade self-improving SQL", "gepa-tuned-sql-agent, CortexKG, ACE/Text2SQL playbook pattern"],
        ],
    )

    doc.add_heading("8.1 Most Practical Cursor Setup Today", level=2)
    add_bullets(
        doc,
        [
            "A database study skill (explore + query)",
            "A memory skill (madb-memory or deep-agents-memory)",
            "A self-improvement skill (self-improving-agent or continuous-learning-v2)",
            "Project files: schema_notes.md, query_patterns.md, glossary.md",
            "An MCP server for live DB access (Neon, Supabase, MotherDuck, etc.)",
        ],
    )

    # Appendix - previous research on popular DB skills
    doc.add_page_break()
    doc.add_heading("Appendix A: Most Popular Database Research Skills (Static)", level=1)
    doc.add_paragraph(
        "From the prior research report — popular skills for one-off database research "
        "(schema exploration, querying, optimization) without built-in continuous learning:"
    )
    add_table(
        doc,
        ["Rank", "Skill", "Installs", "Best for"],
        [
            ["1", "supabase-postgres-best-practices", "264K", "Postgres query tuning, schema design, EXPLAIN"],
            ["2", "lark-base", "339K", "Feishu/Lark multi-dimensional table queries"],
            ["3", "supabase", "149K", "Full Supabase platform including DB schema inspection"],
            ["4", "neon-postgres", "45K", "Serverless Postgres exploration"],
            ["5", "firebase-firestore", "58K", "Document queries and schema design"],
            ["6", "postgresql-table-design", "21K", "Postgres schema review"],
            ["7", "sql-optimization-patterns", "15K", "Cross-engine SQL tuning"],
            ["8", "Database Queries (Agent Mag)", "16K", "Multi-DB NL→SQL with read-only mode"],
            ["9", "postgresql-optimization", "13K", "Postgres-specific performance analysis"],
            ["10", "sql-optimization", "13K", "Cross-DB SQL tuning"],
        ],
    )

    doc.add_heading("Appendix B: Install Commands Reference", level=1)
    add_code_block(
        doc,
        "# Search the registry\n"
        "npx skills find \"database\"\n"
        "npx skills find \"sql\"\n"
        "npx skills find \"postgres\"\n\n"
        "# Browse categories\n"
        "# https://skills.sh/topic/databases\n"
        "# https://agentskill.sh/for/database\n"
        "# https://database-skills.com",
    )

    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = footer.add_run("Generated by Cursor Cloud Agent — Lab Repository")
    fr.italic = True
    fr.font.size = Pt(9)
    fr.font.color.rgb = RGBColor(128, 128, 128)

    return doc


if __name__ == "__main__":
    output = "/workspace/AI-Agent-Database-Skills-Research.docx"
    build_document().save(output)
    print(f"Saved: {output}")
