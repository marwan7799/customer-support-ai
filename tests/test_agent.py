import agent


def test_run_tool_call_rejects_malformed_arguments():
    name, result = agent._run_tool_call(
        {"function": {"name": "get_order_status", "arguments": "not-json"}}
    )
    assert name == "get_order_status"
    assert result["success"] is False


def test_run_tool_call_rejects_unknown_tool():
    name, result = agent._run_tool_call({"function": {"name": "delete_everything", "arguments": {}}})
    assert name == "delete_everything"
    assert result["success"] is False
    assert "Unknown tool" in result["error"]


def test_chat_with_agent_executes_tool_then_returns_answer(monkeypatch):
    responses = iter(
        [
            {
                "message": {
                    "content": "",
                    "tool_calls": [
                        {"function": {"name": "get_order_status", "arguments": {"order_id": "10001"}}}
                    ],
                }
            },
            {"message": {"content": "Order 10001 has been delivered.", "tool_calls": None}},
        ]
    )

    monkeypatch.setattr(agent, "classify_request", lambda message: "ORDER")
    monkeypatch.setattr(agent, "chat", lambda *args, **kwargs: next(responses))

    reply = agent.chat_with_agent("Where is order 10001?")
    assert reply == "Order 10001 has been delivered."


def test_chat_with_agent_handles_model_failure(monkeypatch):
    monkeypatch.setattr(agent, "classify_request", lambda message: "OTHER")

    def fail(*args, **kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(agent, "chat", fail)
    reply = agent.chat_with_agent("Hello")
    assert "trouble reaching" in reply


def test_normalize_history_ignores_invalid_or_empty_turns():
    history = [
        {"role": "user", "content": " hi "},
        {"role": "assistant", "content": ""},
        {"role": "invalid", "content": "ignore me"},
    ]
    assert agent._normalize_history(history) == [{"role": "user", "content": "hi"}]
