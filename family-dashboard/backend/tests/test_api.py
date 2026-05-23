from datetime import date, timedelta


def _make_holder(client, name="Shawn"):
    r = client.post("/api/cardholders", json={"name": name, "color_tag": "#3b82f6"})
    assert r.status_code == 201, r.text
    return r.json()


def _make_card(client, cardholder_id, **overrides):
    payload = {
        "cardholder_id": cardholder_id,
        "issuer": "Amex",
        "name": "Platinum",
        "opened_date": str(date.today() - timedelta(days=100)),
        "annual_fee": 695.0,
        "fee_waived_first_year": False,
        "status": "active",
        "next_fee_date": str(date.today() + timedelta(days=15)),
        "can_close_after_date": str(date.today() + timedelta(days=20)),
    }
    payload.update(overrides)
    r = client.post("/api/cards", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def _make_benefit(client, card_id, amount=15.0, frequency="monthly"):
    r = client.post("/api/benefits", json={
        "card_id": card_id,
        "name": "Uber Cash",
        "amount": amount,
        "frequency": frequency,
        "cycle_type": "statement_month",
        "category": "credit",
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_cardholder_crud(client):
    holder = _make_holder(client)
    assert holder["name"] == "Shawn"
    r = client.get(f"/api/cardholders/{holder['id']}")
    assert r.status_code == 200
    r = client.patch(f"/api/cardholders/{holder['id']}", json={"color_tag": "#ff0000"})
    assert r.json()["color_tag"] == "#ff0000"
    assert client.delete(f"/api/cardholders/{holder['id']}").status_code == 204
    assert client.get(f"/api/cardholders/{holder['id']}").status_code == 404


def test_card_crud(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    assert card["issuer"] == "Amex"
    r = client.get("/api/cards", params={"cardholder_id": holder["id"]})
    assert len(r.json()) == 1


def test_benefit_crud_and_claim(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    benefit = _make_benefit(client, card["id"])
    # Claim
    r = client.post(f"/api/benefits/{benefit['id']}/claim", json={})
    assert r.status_code == 201, r.text
    progress = r.json()
    assert progress["claimed_amount"] == 15.0
    assert progress["period"].startswith(f"{date.today().year:04d}-")


def test_sub_crud(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    r = client.post("/api/sign-up-bonuses", json={
        "card_id": card["id"],
        "required_spend": 6000.0,
        "deadline_date": str(date.today() + timedelta(days=60)),
        "reward_description": "80k MR",
        "current_spend": 1500.0,
    })
    assert r.status_code == 201


def test_reminder_crud(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    r = client.post("/api/reminders", json={
        "card_id": card["id"],
        "title": "Pay annual fee",
        "due_date": str(date.today() + timedelta(days=10)),
    })
    assert r.status_code == 201


def test_dashboard_overview_unclaimed(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    _make_benefit(client, card["id"], amount=15.0)
    r = client.get("/api/dashboard/overview")
    assert r.status_code == 200
    data = r.json()
    assert len(data["unclaimed_this_period"]) == 1
    assert data["family_summary"]["total_amount"] == 15.0
    assert data["family_summary"]["claimed_amount"] == 0.0


def test_dashboard_after_claim(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    benefit = _make_benefit(client, card["id"], amount=15.0)
    client.post(f"/api/benefits/{benefit['id']}/claim", json={})
    data = client.get("/api/dashboard/overview").json()
    assert len(data["unclaimed_this_period"]) == 0
    assert data["family_summary"]["claimed_amount"] == 15.0


def test_dashboard_fee_due_soon(client):
    holder = _make_holder(client)
    _make_card(client, holder["id"],
               next_fee_date=str(date.today() + timedelta(days=15)))
    data = client.get("/api/dashboard/overview").json()
    assert len(data["fee_due_soon"]) == 1


def test_dashboard_sub_gap(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    client.post("/api/sign-up-bonuses", json={
        "card_id": card["id"],
        "required_spend": 6000.0,
        "deadline_date": str(date.today() + timedelta(days=60)),
        "reward_description": "80k MR",
        "current_spend": 1000.0,
    })
    data = client.get("/api/dashboard/overview").json()
    assert len(data["sub_gaps"]) == 1
    assert data["sub_gaps"][0]["remaining_spend"] == 5000.0


def test_cardholder_cards_summary(client):
    holder = _make_holder(client)
    card = _make_card(client, holder["id"])
    _make_benefit(client, card["id"], amount=15.0)
    r = client.get(f"/api/cardholders/{holder['id']}/cards")
    assert r.status_code == 200
    cards = r.json()
    assert len(cards) == 1
    assert cards[0]["period_total"] == 15.0
    assert cards[0]["period_claimed"] == 0.0
    assert len(cards[0]["benefit_summaries"]) == 1


def test_presets(client):
    r = client.get("/api/presets/cards")
    assert r.status_code == 200
    presets = r.json()
    assert any(p["name"] == "Platinum" and p["issuer"] == "Amex" for p in presets)
    assert any(p["name"] == "Sapphire Reserve" for p in presets)
