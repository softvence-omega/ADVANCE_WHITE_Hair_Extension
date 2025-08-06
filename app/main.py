import os
from fastapi import FastAPI
from app.routes.hair_extension import router as hair_router  # adjust import path
from app.routes.product_upload import router as product_upload_router

app = FastAPI()

# Mount the hair router under /hair
app.include_router(hair_router, prefix="/hair")
app.include_router(product_upload_router, prefix="/product")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Hair Extension Color Matcher API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 1000))  # ✅ Render sets PORT dynamically
    uvicorn.run(app, host="0.0.0.0", port=port)
