import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from app.routes.hair_extension import router as hair_router
from app.routes.product_upload import router as product_upload_router
import time

app = FastAPI()

# CORS middleware (if you need cross-origin requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://advancewhite.netlify.app", "http://127.0.0.1:5501","https://naturylextensions.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
