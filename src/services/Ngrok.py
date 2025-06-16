import aiohttp

from src.config import NGROK_API_KEY
from src.dependencies import logger


class Ngrok:
    def __init__(self):
        self.endpoint = "https://api.ngrok.com/"

    async def get_tunnels(self):
        tunnels_endpoint = f"{self.endpoint}/tunnels"
        headers = {
            "Authorization": f"Bearer {NGROK_API_KEY}",
            "Ngrok-Version": "2"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(tunnels_endpoint, headers=headers) as response:
                data = await response.json()

        logger.debug(f"Ngrok tunnels: {data}")
        tunnels = data.get("tunnels", [])
        return tunnels

    async def get_public_urls(self):
        tunnels = await self.get_tunnels()
        public_urls = [tunnel["public_url"] for tunnel in tunnels if "public_url" in tunnel]
        return public_urls
