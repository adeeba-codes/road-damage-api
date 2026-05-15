from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class ComplaintDB:
    @staticmethod
    async def create_complaint(title, description, latitude, longitude, category, reported_by):
        """Create a new complaint with geospatial data"""
        response = supabase.table("complaints").insert({
            "title": title,
            "description": description,
            "latitude": latitude,
            "longitude": longitude,
            "location_geom": f"POINT({longitude} {latitude})",  # PostGIS format
            "category": category,
            "reported_by": reported_by,
            "status": "Open",
            "reported_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None

    @staticmethod
    async def upload_photo(complaint_id, file):
        """Upload photo to Supabase Storage"""
        file_path = f"complaints/{complaint_id}.jpg"
        response = supabase.storage.from_("complaint-photos").upload(
            file_path,
            file.file.read(),
            {"content-type": "image/jpeg"}
        )
        
        # Get public URL
        photo_url = supabase.storage.from_("complaint-photos").get_public_url(file_path)
        
        # Update complaint with photo URL
        supabase.table("complaints").update({"photo_url": photo_url}).eq("id", complaint_id).execute()
        return photo_url

    @staticmethod
    async def get_all_complaints():
        """Get all complaints for map view"""
        response = supabase.table("complaints").select("*").execute()
        return response.data

    @staticmethod
    async def get_complaints_by_status(status):
        """Get complaints filtered by status"""
        response = supabase.table("complaints").select("*").eq("status", status).execute()
        return response.data

    @staticmethod
    async def update_complaint_status(complaint_id, status, admin_notes=None):
        """Update complaint status (admin only)"""
        update_data = {"status": status}
        if admin_notes:
            update_data["admin_notes"] = admin_notes
        if status == "Resolved":
            update_data["resolved_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("complaints").update(update_data).eq("id", complaint_id).execute()
        return response.data[0] if response.data else None

    @staticmethod
    async def get_complaints_near(latitude, longitude, radius_km=5):
        """Get complaints within X km (PostGIS query)"""
        response = supabase.rpc(
            "get_nearby_complaints",
            {
                "user_lat": latitude,
                "user_lon": longitude,
                "radius_meters": radius_km * 1000
            }
        ).execute()
        return response.data