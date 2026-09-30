from app.models import StoryPanel


def build_comic_layout(story, image_paths):
    layout = []

    for panel, image_path in zip(story, image_paths):
        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "scene_description": panel.scene_description,
                "caption": panel.caption,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
                "image_url": image_path,
            }
        )

    return layout
