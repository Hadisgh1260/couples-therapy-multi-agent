import asyncio
import os

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from prompts import therapist_prompt

load_dotenv()

GATEWAY_URL = os.getenv("GATEWAY_URL")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY")

THERAPIST_GROQ_API_KEY = os.getenv("THERAPIST_GROQ_API_KEY")
THERAPIST_MODEL = os.getenv("THERAPIST_MODEL")


async def main():

    client = OpenAIChatCompletionClient(
        model=THERAPIST_MODEL,
        api_key=GATEWAY_API_KEY,
        base_url=f"{GATEWAY_URL}/v1",

        default_headers={
            "X-Groq-API-Key": THERAPIST_GROQ_API_KEY,
        },

        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown",
        },
    )

    therapist = AssistantAgent(
        name="Therapist",
        model_client=client,
        system_message=therapist_prompt,
    )

    conversation = """
Sara: I feel like Reza doesn't pay enough attention to me.
When I try to talk about things that matter to me,
he looks away or goes back to his phone or TV.
I feel invisible and like I'm the only one who cares.

Reza: I think Sara expects too much from me.
She wants me to be the provider, the planner,
and emotional support all the time.
I work hard and I don't have the bandwidth to be everything for her.

Therapist:
"""

    result = await therapist.run(
        task=(
            "Analyze the following couples therapy conversation "
            "and respond as the therapist. "
            "Identify the main conflict, the needs of both partners, "
            "and ask a useful follow-up question that could help "
            "move the session forward.\n\n"
            + conversation
        )
    )

    for message in result.messages:
        print("\nSOURCE:", message.source)
        print("CONTENT:", message.content)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())