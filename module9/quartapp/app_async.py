import asyncio
from quart import Quart, jsonify, request

app = Quart(__name__)

@app.route("/")
async def home():
    return jsonify({"Message":"Welcome home"})

@app.route("/slow")
async def slow_task():
    await asyncio.sleep(3)
    return jsonify({"Message":"This was the slow process"})

@app.route("/parallel")
async def parrallel_task():
    async def task(id):
        await asyncio.sleep(2)
        return f"Task {id} done"
    
    results = await asyncio.gather(task(1), task(2), task(3))
    return jsonify({"results": results})

@app.route("/external")
async def call_external():
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.github.com") as resp:
            data = await resp.json()
            return jsonify({"Github API status": resp.status, "headers" : list(data.keys()) [:5]})
if __name__ == "__main__":
    app.run(port=5000)