from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import ComplaintDB
from app.models import ComplaintCreate, ComplaintUpdate, ComplaintResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Road Damage API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://road-damage-app.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CITIZEN ENDPOINTS =====

@app.post("/api/complaints")
async def create_complaint(complaint: ComplaintCreate):
    """Create new complaint"""
    try:
        result = await ComplaintDB.create_complaint(
            complaint.title,
            complaint.description,
            complaint.latitude,
            complaint.longitude,
            complaint.category,
            complaint.reported_by
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

@app.post("/api/complaints/{complaint_id}/photo")
async def upload_complaint_photo(complaint_id: str, file: UploadFile = File(...)):
    """Upload photo for a complaint"""
    try:
        photo_url = await ComplaintDB.upload_photo(complaint_id, file)
        return {"status": "success", "photo_url": photo_url}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

@app.get("/api/complaints")
async def get_all_complaints():
    """Get all complaints for map display"""
    try:
        complaints = await ComplaintDB.get_all_complaints()
        return {"status": "success", "data": complaints}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

@app.get("/api/complaints/status/{status}")
async def get_complaints_by_status(status: str):
    """Get complaints filtered by status"""
    try:
        complaints = await ComplaintDB.get_complaints_by_status(status)
        return {"status": "success", "data": complaints}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

# ===== ADMIN ENDPOINTS =====

@app.put("/api/admin/complaints/{complaint_id}")
async def update_complaint(complaint_id: str, update: ComplaintUpdate):
    """Update complaint status (admin)"""
    try:
        result = await ComplaintDB.update_complaint_status(
            complaint_id,
            update.status,
            update.admin_notes
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Admin dashboard stats"""
    try:
        open_complaints = await ComplaintDB.get_complaints_by_status("Open")
        in_progress = await ComplaintDB.get_complaints_by_status("In Progress")
        resolved = await ComplaintDB.get_complaints_by_status("Resolved")
        
        return {
            "status": "success",
            "stats": {
                "total_open": len(open_complaints),
                "total_in_progress": len(in_progress),
                "total_resolved": len(resolved),
                "total_all": len(open_complaints) + len(in_progress) + len(resolved)
            },
            "data": {
                "open": open_complaints,
                "in_progress": in_progress,
                "resolved": resolved
            }
        }
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

@app.get("/health")
async def health_check():
    return {"status": "ok"}