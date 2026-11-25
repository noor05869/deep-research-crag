from types import SimpleNamespace
from unittest.mock import Mock

from deep_research import evaluator, grader, tools


def draft():
    return {
        "raw_query": "How long is the loan, and who approves it?",
        "documents": [{"source": "Policy", "content": "Loans last 60 days."}],
        "final_response": "Loans last 60 days [1].",
        "citations": [{"citation_id": "[1]", "source": "Policy", "quote": "Loans last 60 days."}],
    }


def test_audit_failure_at_limit_withholds_draft(monkeypatch):
    monkeypatch.setattr(evaluator, "build_evaluators", Mock(side_effect=TimeoutError))
    state = {**draft(), "loop_step": 3}
    result = evaluator.check_hallucination_node(state)
    assert result["hallucination_grade"] == "audit_failed"
    assert result["final_response"] != state["final_response"]
    assert result["citations"] == []


def test_invalid_citation_is_rejected_before_model_audit(monkeypatch):
    build = Mock(side_effect=AssertionError("Invalid citation reached model audit"))
    monkeypatch.setattr(evaluator, "build_evaluators", build)
    state = draft()
    state["citations"][0]["quote"] = "Loans last 30 days."
    assert evaluator.check_hallucination_node(state)["hallucination_grade"] == "hallucinated"
    build.assert_not_called()


def test_valid_citation_uses_retrieved_source(monkeypatch):
    grounding = Mock()
    grounding.invoke.return_value = SimpleNamespace(binary_score="grounded", explanation="Supported")
    relevance = Mock()
    relevance.invoke.return_value = SimpleNamespace(binary_score="yes", explanation="Complete")
    monkeypatch.setattr(evaluator, "build_evaluators", lambda: (grounding, relevance))
    state = draft()
    state["raw_query"] = "How long is the loan?"
    state["citations"][0]["source"] = "Model-generated source"
    result = evaluator.check_hallucination_node(state)
    assert result["hallucination_grade"] == "grounded"
    assert result["citations"][0]["source"] == "Policy"
    assert "[1] Source: Policy" in grounding.invoke.call_args.args[0]["documents"]


def test_partial_coverage_targets_the_missing_evidence(monkeypatch):
    relevance = Mock()
    relevance.invoke.return_value = SimpleNamespace(binary_score="yes", reasoning="Loan duration")
    monkeypatch.setattr(grader, "build_document_grader", lambda: relevance)
    coverage = Mock()
    coverage.invoke.return_value = SimpleNamespace(missing_evidence="Who approves the loan?")
    monkeypatch.setattr(grader, "build_coverage_grader", lambda: coverage, raising=False)
    state = draft()
    update = grader.grade_documents_node(state)
    assert update["web_search_needed"]
    assert update["documents"] == state["documents"]
    rewriter = Mock()
    rewriter.invoke.return_value = SimpleNamespace(search_query="loan approval authority", rationale="Coverage gap")
    monkeypatch.setattr(tools, "build_query_rewriter", lambda: rewriter)
    assert tools.transform_query_node({**state, **update})["transformed_query"] == "loan approval authority"
    assert rewriter.invoke.call_args.args[0]["missing_evidence"] == "Who approves the loan?"
