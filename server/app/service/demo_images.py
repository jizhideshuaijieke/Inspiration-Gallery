def build_demo_image_url(task_id: int, style_id: int) -> str:
    # Stable public placeholder image for local demo.
    return f"https://picsum.photos/seed/style-{style_id}-task-{task_id}/1024/1024"
