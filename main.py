import asyncio
import os
import random

import openai
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from profiles import woman_profile, man_profile
from prompts import woman_prompt, man_prompt, therapist_prompt


load_dotenv()


# =========================
# Environment Variables
# =========================

GATEWAY_URL = os.getenv("GATEWAY_URL")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY")

WOMAN_GROQ_API_KEY = os.getenv("WOMAN_GROQ_API_KEY")
MAN_GROQ_API_KEY = os.getenv("MAN_GROQ_API_KEY")
THERAPIST_GROQ_API_KEY = os.getenv("THERAPIST_GROQ_API_KEY")

WOMAN_MODEL = os.getenv("WOMAN_MODEL")
MAN_MODEL = os.getenv("MAN_MODEL")
THERAPIST_MODEL = os.getenv("THERAPIST_MODEL")


# =========================
# Retry Helper
# =========================
# The gateway sits behind a shared Cloudflare Worker that intermittently
# returns 403 Forbidden or times out under certain request patterns, even
# though the key/gateway themselves are valid. This wrapper retries with
# exponential backoff + jitter so a single flaky call doesn't kill the
# whole session.

MAX_RETRIES = 5
BASE_DELAY = 3  # seconds


async def run_with_retry(agent, task, max_retries=MAX_RETRIES, base_delay=BASE_DELAY):

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return await agent.run(task=task)

        except (openai.APITimeoutError, openai.PermissionDeniedError, openai.APIConnectionError) as e:
            last_error = e
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1.5)

            print(
                f"[retry] {agent.name} call failed "
                f"({type(e).__name__}), attempt {attempt}/{max_retries}. "
                f"Retrying in {delay:.1f}s..."
            )

            if attempt < max_retries:
                await asyncio.sleep(delay)

    raise last_error


# =========================
# Create Client
# =========================

def create_client(model, groq_api_key):

    return OpenAIChatCompletionClient(
        model=model,
        api_key=GATEWAY_API_KEY,
        base_url=f"{GATEWAY_URL}/v1",

        # Give the shared gateway more time to respond, and let the
        # underlying OpenAI SDK do a couple of quick retries of its own
        # before we fall back to our own slower retry loop above.
        timeout=90,
        max_retries=1,

        default_headers={
            "X-Groq-API-Key": groq_api_key,
        },

        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown",
        },
    )


# =========================
# Main
# =========================

async def main():

    print("Creating model clients...")

    woman_client = create_client(
        WOMAN_MODEL,
        WOMAN_GROQ_API_KEY,
    )

    man_client = create_client(
        MAN_MODEL,
        MAN_GROQ_API_KEY,
    )

    therapist_client = create_client(
        THERAPIST_MODEL,
        THERAPIST_GROQ_API_KEY,
    )


    print("Creating agents...")


    # =========================
    # Woman Agent
    # =========================

    woman = AssistantAgent(
        name="Woman",
        model_client=woman_client,
        system_message=woman_prompt(woman_profile),
    )


    # =========================
    # Man Agent
    # =========================

    man = AssistantAgent(
        name="Man",
        model_client=man_client,
        system_message=man_prompt(man_profile),
    )


    # =========================
    # Therapist Agent
    # =========================

    therapist = AssistantAgent(
        name="Therapist",
        model_client=therapist_client,
        system_message=therapist_prompt,
    )


    print("Starting therapy session...")

    print("\n" + "=" * 60)
    print("COUPLES THERAPY SESSION")
    print("=" * 60)


    # =========================
    # Initial Situation
    # =========================

    sara_message = """
The therapy session has started.

The therapist asks Sara:

"What is the main problem you are experiencing
in your relationship with Reza?"

Answer naturally in character.
"""


    # =========================
    # Sara
    # =========================

    sara_result = await run_with_retry(woman, sara_message)

    sara = sara_result.messages[-1].content

    print("\n[Woman - Sara]")
    print(sara)


    # =========================
    # Reza
    # =========================

    reza_message = f"""
The couples therapy session has started.

Sara said:

"{sara}"

Now answer as Reza.

The therapist asks:

"Reza, what is your perspective on this problem?"

Respond naturally in character according to your profile.
"""

    reza_result = await run_with_retry(man, reza_message)

    reza = reza_result.messages[-1].content

    print("\n[Man - Reza]")
    print(reza)


    # =========================
    # Therapist - First Analysis
    # =========================

    therapist_message = f"""
You are conducting a couples therapy session.

Sara said:

"{sara}"

Reza said:

"{reza}"

Analyze what both partners said.

Identify:
- the main conflict
- Sara's emotional needs
- Reza's emotional needs
- the communication pattern

Then ask ONE useful follow-up question to continue
the therapy session.

Do not produce the final report yet.
"""

    therapist_result = await run_with_retry(therapist, therapist_message)

    therapist_response = therapist_result.messages[-1].content

    print("\n[Therapist]")
    print(therapist_response)


    # =========================
    # Second Round - Sara
    # =========================

    sara_result_2 = await run_with_retry(
        woman,
        f"""
The therapist said:

"{therapist_response}"

Respond to the therapist's question naturally
as Sara.

Stay in character and explain your feelings
and perspective.
""",
    )

    sara_2 = sara_result_2.messages[-1].content

    print("\n[Woman - Sara]")
    print(sara_2)


    # =========================
    # Second Round - Reza
    # =========================

    reza_result_2 = await run_with_retry(
        man,
        f"""
The therapist said:

"{therapist_response}"

Sara then said:

"{sara_2}"

Respond naturally as Reza.

Stay in character and explain your feelings
and perspective.
""",
    )

    reza_2 = reza_result_2.messages[-1].content

    print("\n[Man - Reza]")
    print(reza_2)


    # =========================
    # Final Therapist Report
    # =========================

    final_therapist_prompt = f"""
You are the therapist conducting a couples therapy session.

Here is the complete conversation so far.

SARA - FIRST:
{sara}

REZA - FIRST:
{reza}

THERAPIST:
{therapist_response}

SARA - SECOND:
{sara_2}

REZA - SECOND:
{reza_2}


Now analyze the complete session.

Produce the final therapy session report.

The report must contain:

1. Main conflict
2. Woman's perspective
3. Man's perspective
4. Emotional needs
5. Communication problems
6. Main patterns identified
7. Therapist's observations
8. Recommended next steps

Remain neutral and do not take sides.

After the report, write:

SESSION_COMPLETE
"""


    final_result = await run_with_retry(therapist, final_therapist_prompt)

    final_report = final_result.messages[-1].content

    print("\n" + "=" * 60)
    print("[THERAPIST - FINAL REPORT]")
    print("=" * 60)

    print(final_report)


    # =========================
    # Close Clients
    # =========================

    await woman_client.close()
    await man_client.close()
    await therapist_client.close()


# =========================
# Run
# =========================

if __name__ == "__main__":
    asyncio.run(main())
