from pydantic import BaseModel, EmailStr

USER_STATUS_ACTIVE = "active"
USER_STATUS_DEACTIVATED = "deactivated"

# User data model


class UserModel(BaseModel):
    name: str
    picture: str
    user_id: str
    email: EmailStr
    current_plan: str = ""
    enterprise_id: str = ""
    status: str = USER_STATUS_ACTIVE


class UserStatsModel(BaseModel):
    cloud_ocr_per_month: int = 0
    translation_per_month: int = 0
    trash_data_storage_days: int = 0
    file_capacity: int = 0
    cloud_space_total_file: int = 0
    cloud_space_total_size: int = 0
    cloud_space_total_folder: int = 0
    remove_ads_and_watermark: bool = False
    pdf_manipulation_per_month: int = 0
    file_conversion_per_month: int = 0
    image_to_docx_per_month: int = 0
    image_to_pdf_per_month: int = 0
    text_to_docx_per_month: int = 0
    text_to_pdf_per_month: int = 0

class UpgradeDTO(BaseModel):
    plan: str