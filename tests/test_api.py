from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.anyio
async def test_list_actors(client: AsyncClient):
    r = await client.get("/api/v1/actors?page=1&size=5")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert body["total"] > 0
    assert len(body["items"]) <= 5


@pytest.mark.anyio
async def test_get_actor(client: AsyncClient):
    r = await client.get("/api/v1/actors/1")
    assert r.status_code == 200
    assert "actor_id" in r.json()


@pytest.mark.anyio
async def test_actor_not_found(client: AsyncClient):
    r = await client.get("/api/v1/actors/999999")
    assert r.status_code == 404


@pytest.mark.anyio
async def test_search_actors_by_name(client: AsyncClient):
    r = await client.get("/api/v1/actors?name=Penelope")
    assert r.status_code == 200
    items = r.json()["items"]
    assert any("Penelope" in (i["first_name"] + i["last_name"]) for i in items)


@pytest.mark.anyio
async def test_list_films(client: AsyncClient):
    r = await client.get("/api/v1/films?page=1&size=3")
    assert r.status_code == 200
    assert r.json()["total"] > 0


@pytest.mark.anyio
async def test_get_film_detail(client: AsyncClient):
    r = await client.get("/api/v1/films/1")
    assert r.status_code == 200
    body = r.json()
    assert "actors" in body
    assert "categories" in body
    assert "language_rel" in body


@pytest.mark.anyio
async def test_filter_films_by_rating(client: AsyncClient):
    r = await client.get("/api/v1/films?rating=PG")
    assert r.status_code == 200
    for film in r.json()["items"]:
        assert film["rating"] == "PG"


@pytest.mark.anyio
async def test_list_customers(client: AsyncClient):
    r = await client.get("/api/v1/customers?page=1&size=5")
    assert r.status_code == 200
    assert r.json()["total"] > 0


@pytest.mark.anyio
async def test_payment_summary(client: AsyncClient):
    r = await client.get("/api/v1/payments/summary")
    assert r.status_code == 200
    body = r.json()
    assert "total_revenue" in body
    assert body["total_payments"] > 0


@pytest.mark.anyio
async def test_overdue_rentals(client: AsyncClient):
    r = await client.get("/api/v1/rentals/overdue?page=1&size=5")
    assert r.status_code == 200
    assert "items" in r.json()


@pytest.mark.anyio
async def test_list_categories(client: AsyncClient):
    r = await client.get("/api/v1/categories")
    assert r.status_code == 200
    assert len(r.json()) > 0


@pytest.mark.anyio
async def test_list_languages(client: AsyncClient):
    r = await client.get("/api/v1/languages")
    assert r.status_code == 200
    assert len(r.json()) > 0


@pytest.mark.anyio
async def test_inventory_available(client: AsyncClient):
    r = await client.get("/api/v1/inventory/available?film_id=1")
    assert r.status_code == 200


@pytest.mark.anyio
async def test_customer_rentals(client: AsyncClient):
    r = await client.get("/api/v1/customers/1/rentals?size=5")
    assert r.status_code == 200
    assert "items" in r.json()
