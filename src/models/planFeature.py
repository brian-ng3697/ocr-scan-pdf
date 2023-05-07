from pydantic import BaseModel

# Base plan feature (Free)


class PlanFeature(BaseModel):
    name: str  # FREE - PREMIUM - BUSINESS
    # OCR
    cloud_ocr_per_month: int = 5  # Quality will be define by package type

    # CLOUD INTERACTION
    trash_data_storage_days: int = 7
    file_capacity: int = 5 * 1048576  # 5Mb
    cloud_space_total_file: int = 100
    cloud_space_total_folder: int = 3

    # TRANSLATION
    translation_per_month = 100

    # FILE CONVERTION
    # word_to_pdf: bool = True
    file_conversion_per_month = 10

    # IMAGE CONVERTION
    image_to_docx_per_month: int = 5
    image_to_pdf_per_month = 10
    image_to_excel_per_month = 10  # consideration

    # TEXT CONVERTION
    text_to_docx_per_month = 10
    text_to_pdf_per_month = 10

    # PDF MANIPULATION
    # including all actions (delete, rotation, merge, split, sort, etc.)
    pdf_manipulation_per_month = 10

    # ELSE
    remove_ads_and_watermark: bool = False
    hands_writing_detection: bool = False
    custom_model_training: int = 0

FREE_PLAN_FEATURE = PlanFeature(
    name="free",
    # OCR
    cloud_ocr_per_month=12,
    # Translation
    translation_per_month=12,
    # CLOUD INTERACTION
    file_capacity=2 * 1048576,  # 2Mb
    cloud_space_total_file=100,
    trash_data_storage_days=7,  # 7 days
    # FOLDER
    cloud_space_total_folder=3,
    # WATERMARK
    remove_ads_and_watermark=False
)

PREMIUM_PLAN_FEATURE = PlanFeature(
    name="premium",
    # OCR
    cloud_ocr_per_month=100,
    # Translation
    translation_per_month=100,
    # CLOUD INTERACTION
    trash_data_storage_days=30,  # 30 days
    file_capacity=5 * 1048576,  # 5Mb
    cloud_space_total_file=1000,
    # FOLDER
    cloud_space_total_folder=20,
    # WATERMARK
    remove_ads_and_watermark=True,
    # PDF MANIPULATION
    pdf_manipulation_per_month=10,
    # FILE CONVERTION
    file_conversion_per_month=10,
    # IMAGE CONVERTION
    image_to_docx_per_month=10,
    image_to_pdf_per_month=10,
    # TEXT CONVERTION
    text_to_docx_per_month=10,
    text_to_pdf_per_month=10
)

BUSSINESS_PLAN_FEATURE = PlanFeature(
    name="business"
)
