import pytest

@pytest.mark.asyncio
async def test_message_generation_approval_and_sending_flow(async_client, auth_headers):
    # 1. Fetch contacts
    contacts_resp = await async_client.get("/api/v1/contacts", headers=auth_headers)
    assert contacts_resp.status_code == 200
    contacts = contacts_resp.json()
    assert len(contacts) > 0
    contact = contacts[0]

    # 2. Duplicate check before drafting
    dup_resp = await async_client.get(
        f"/api/v1/outreach/duplicate-check?contact_id={contact['id']}",
        headers=auth_headers
    )
    assert dup_resp.status_code == 200

    # 3. Generate Outreach Draft
    gen_payload = {
        "contact_id": contact["id"],
        "channel": "LINKEDIN_CONNECT",
        "strategy": "RECRUITER"
    }
    gen_resp = await async_client.post("/api/v1/outreach/generate", json=gen_payload, headers=auth_headers)
    assert gen_resp.status_code == 200
    draft = gen_resp.json()
    assert draft["status"] == "DRAFT"
    assert "2028" in draft["content"]
    assert draft["approved_at"] is None
    draft_id = draft["id"]

    # 4. Human Approval: Edit and Approve
    approve_payload = {
        "approved_by": "Arjun Mehta",
        "edited_content": draft["content"] + " Looking forward to hearing from you!"
    }
    appr_resp = await async_client.post(
        f"/api/v1/outreach/{draft_id}/approve",
        json=approve_payload,
        headers=auth_headers
    )
    assert appr_resp.status_code == 200
    approved_item = appr_resp.json()
    assert approved_item["status"] == "APPROVED"
    assert approved_item["approved_at"] is not None
    assert approved_item["message_version"] == 2

    # 5. Mark Sent
    sent_resp = await async_client.post(f"/api/v1/outreach/{draft_id}/sent", headers=auth_headers)
    assert sent_resp.status_code == 200
    sent_item = sent_resp.json()
    assert sent_item["status"] == "SENT"
    assert sent_item["sent_at"] is not None

    # 6. Verify Follow-up was scheduled
    fu_resp = await async_client.get("/api/v1/followups", headers=auth_headers)
    assert fu_resp.status_code == 200
    followups = fu_resp.json()
    assert any(f["outreach_id"] == draft_id for f in followups)
