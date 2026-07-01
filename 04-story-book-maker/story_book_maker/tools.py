import base64

from google.adk.tools.tool_context import ToolContext
from google.genai import types
from openai import OpenAI


async def generate_illustrations(tool_context: ToolContext):
    """State 의 story_book 을 읽어 각 페이지 삽화를 생성하고 Artifact 로 저장한다."""

    story = tool_context.state.get("story_book")
    if not story:
        return {"status": "error", "message": "State 에 story_book 데이터가 없습니다."}

    client = OpenAI()
    pages = story.get("pages", [])
    existing = await tool_context.list_artifacts()

    results = []
    for page in pages:
        page_number = page.get("page_number")
        visual = page.get("visual_description", "")
        filename = f"page_{page_number}.jpeg"

        # 이미 생성된 페이지는 건너뛴다.
        if filename in existing:
            results.append({"page_number": page_number, "filename": filename})
            continue

        image = client.images.generate(
            model="gpt-image-1",
            prompt=(
                "Children's storybook illustration, soft warm friendly art style, "
                f"high quality: {visual}"
            ),
            n=1,
            size="1024x1024",
            quality="low",
            output_format="jpeg",
        )

        image_bytes = base64.b64decode(image.data[0].b64_json)

        artifact = types.Part(
            inline_data=types.Blob(
                mime_type="image/jpeg",
                data=image_bytes,
            )
        )

        await tool_context.save_artifact(filename=filename, artifact=artifact)

        results.append({"page_number": page_number, "filename": filename})

    return {
        "total_images": len(results),
        "images": results,
        "status": "complete",
    }
