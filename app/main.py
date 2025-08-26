import os
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from app.routes.hair_extension import router as hair_router
from app.routes.product_upload import router as product_upload_router
import time

app = FastAPI()

# CORS middleware (if you need cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://advancewhite.netlify.app"],  # Replace with your allowed origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware example: logging request time
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"{request.method} {request.url} completed in {process_time:.4f}s")
    return response

# Include routers
app.include_router(hair_router, prefix="/hair")
app.include_router(product_upload_router, prefix="/product")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Hair Extension Color Matcher API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 1000))
    uvicorn.run(app, host="0.0.0.0", port=port)
