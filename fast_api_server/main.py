from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fast_api_server.local_inference import generate_response

app = FastAPI()

app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],  # Lock down in production
		allow_methods=["*"],
		allow_headers=["*"],
		allow_credentials=True)


@app.post("/api/generate")
async def generate(req: Request):
	data = await req.json()
	prompt = data.get("prompt", "")
	result = generate_response(prompt)
	return JSONResponse(content={"response": result})
