from src.app.agent.MruNav_agent import agent


async def start_agent_session():
    session_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        create_session(db, session_id, "John Doe")
    finally:
        db.close()
    final_state = await agent.ainvoke(
        {"user_name": "John Doe"},
        config={"configurable": {"thread_id": session_id}},
    )
    snapshot = serialize_state(final_state)
    update_session_snapshot(session_id, snapshot)

    last_message = final_state["messages"][-1].content
    return {
        "session_id": session_id,
        "last_message": last_message,
    }

async def agent_continue(req: FriaAgentInvokeSchema):
    resume_payload = {}

    if req.user_message is not None:
        resume_payload["user_message"] = req.user_message

    if req.lat is not None and req.lon is not None:
        resume_payload["lat"] = req.lat
        resume_payload["lon"] = req.lon

    final_state = await agent.ainvoke(
        Command(resume=resume_payload),
        config={"configurable": {"thread_id": str(req.session_id)}},
    )

    snapshot = serialize_state(final_state)
    update_session_snapshot(str(req.session_id), snapshot)

    last_message = final_state["messages"][-1].content
    return {"last_message": last_message}