from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=3, max_length=2000)
    character_name: str = Field(..., min_length=1, max_length=100)
    setting: str = Field(..., min_length=1, max_length=100)
    tone: str = Field(default="light-hearted", max_length=50)
    art_style: str = Field(default="comic book", max_length=100)


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class StoryPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str
    image_url: str = ""
