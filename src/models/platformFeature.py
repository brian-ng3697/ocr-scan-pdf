from pydantic import BaseModel

# Base platform feature 
class PlatformFeature(BaseModel):
    name: str


APP_PLATFORM_FEATURE = PlatformFeature(
    name="app"
)

WEB_PLATFORM_FEATURE = PlatformFeature(
    name="web",
)
