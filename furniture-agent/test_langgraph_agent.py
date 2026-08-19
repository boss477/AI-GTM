import agno_agent


def test_parse_request_extracts_city_segment_and_limit():
    request = agno_agent.parse_request(
        "Find hotel furniture leads in Chennai, limit to 5 results"
    )

    assert request == {"city": "Chennai", "segment": "Hotel", "limit": 5}


def test_run_agent_executes_langgraph_workflow(monkeypatch):
    leads = [
        {
            "company": "Hotel One",
            "website": "https://hotel.one",
            "intent_signal": "Grand opening",
            "intent_score": 10,
            "city": "Chennai",
            "segment": "Hotel",
        }
    ]
    save_result = {"success": True, "message": "Saved 1 leads", "count": 1}

    monkeypatch.setattr(agno_agent, "search_leads_direct", lambda **kwargs: leads)
    monkeypatch.setattr(agno_agent, "score_leads_direct", lambda value: value)
    monkeypatch.setattr(
        agno_agent,
        "filter_high_intent_leads_direct",
        lambda value, min_score=7: {
            "high_intent_leads": value,
            "medium_intent_leads": [],
            "low_intent_leads": [],
            "summary": "Found 1 high-intent (9-10), 0 medium (7-8), 0 low (below 7)",
        },
    )
    monkeypatch.setattr(agno_agent, "save_leads_direct", lambda value: save_result)

    response = agno_agent.run_agent("Find hotel furniture leads in Chennai, limit to 5")

    assert "Hotel One" in response.content
    assert "Chennai" in response.content
    assert response.state["save_result"] == save_result
