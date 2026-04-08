import cloudinary
import cloudinary.uploader
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_xray(image_bytes: bytes, filename: str = "xray") -> str:
    """Upload X-ray image bytes to Cloudinary and return the secure URL."""
    result = cloudinary.uploader.upload(
        image_bytes,
        folder="dentai/xrays",
        public_id=filename,
        resource_type="image",
        overwrite=False,
        unique_filename=True,
    )
    return result["secure_url"]
