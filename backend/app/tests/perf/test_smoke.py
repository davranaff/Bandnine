import asyncio

import pytest


@pytest.mark.asyncio
async def test_concurrent_health_smoke(client):
    tasks = [client.get("/health") for _ in range(20)]
    responses = await asyncio.gather(*tasks)
    assert all(response.status_code == 200 for response in responses)
