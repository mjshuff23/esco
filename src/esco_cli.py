"""Minimal CLI for the offline interactive ESCO lane."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from esco_orchestrator import OrchestratorOutcome, build_demo_orchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local ESCO demo lane against the repo corpus.")
    parser.add_argument("prompt", nargs="*", help="One-shot prompt. Omit to start interactive mode.")
    parser.add_argument("--interactive", action="store_true", help="Start a simple REPL.")
    parser.add_argument("--limit", type=int, default=3, help="Maximum number of evidence chunks to retrieve.")
    parser.add_argument(
        "--no-consequences",
        action="store_true",
        help="Skip the consequences-mode analysis in the orchestrator result.",
    )
    return parser


def render_outcome(outcome: OrchestratorOutcome) -> str:
    lines = [
        f"Route: {outcome.verification.route_decision.route or 'Conversational'}",
        f"Policy: {outcome.ethics_decision.outcome}",
    ]
    if outcome.verification.route_decision.claim is not None:
        lines.append(f"Claim: {outcome.verification.route_decision.claim.claim_text}")

    lines.extend(
        [
            "",
            "Answer:",
            outcome.answer_text or "(no generated text)",
        ]
    )

    if outcome.verification.support_profile is not None:
        lines.extend(["", f"Support Profile: {outcome.verification.support_profile.overall_posture}"])
        for field_name, metric in outcome.verification.support_profile.metrics.items():
            lines.append(f"- {field_name}: {metric.score_band} ({metric.rationale})")
        for caveat in outcome.verification.support_profile.caveats:
            lines.append(f"- caveat: {caveat}")

    if outcome.evidence_records:
        lines.append("")
        lines.append("Evidence:")
        for index, record in enumerate(outcome.evidence_records, start=1):
            excerpt = _collapse_whitespace(record.excerpt, max_length=180)
            lines.append(f"{index}. {excerpt}")
            lines.append(f"   source: {record.provenance.canonical_url}")

    if outcome.verification.consequences is not None:
        lines.append("")
        lines.append("Consequences If False:")
        for effect in outcome.verification.consequences.downstream_effects:
            lines.append(f"- {effect}")

    return "\n".join(lines)


def run_once(prompt: str, *, retrieval_limit: int = 3, include_consequences: bool = True) -> OrchestratorOutcome:
    orchestrator = build_demo_orchestrator()
    return orchestrator.handle_prompt(
        prompt,
        retrieval_limit=retrieval_limit,
        include_consequences=include_consequences,
    )


def run_repl(*, retrieval_limit: int = 3, include_consequences: bool = True) -> int:
    orchestrator = build_demo_orchestrator()
    print("ESCO local demo. Type 'exit' or 'quit' to stop.")
    while True:
        try:
            prompt = input("\nesco> ").strip()
        except EOFError:
            print()
            return 0
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            return 0
        outcome = orchestrator.handle_prompt(
            prompt,
            retrieval_limit=retrieval_limit,
            include_consequences=include_consequences,
        )
        print(render_outcome(outcome))


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    include_consequences = not args.no_consequences

    if args.interactive or not args.prompt:
        return run_repl(
            retrieval_limit=args.limit,
            include_consequences=include_consequences,
        )

    outcome = run_once(
        " ".join(args.prompt),
        retrieval_limit=args.limit,
        include_consequences=include_consequences,
    )
    print(render_outcome(outcome))
    return 0


def _collapse_whitespace(text: str, *, max_length: int) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= max_length:
        return collapsed
    return f"{collapsed[: max_length - 3].rstrip()}..."


if __name__ == "__main__":
    raise SystemExit(main())
