import json

from recon.llm import get_llm

SYSTEM_PROMPT = """You are a data reconciliation analyst. You are given the results of an
automated comparison between two dataset exports. The findings are already computed and
factual: do not invent, recompute, or add any transactions or numbers that are not present
in the findings.

Write a concise report that:
- States whether the two sources reconcile.
- Groups the issues by type (missing records, duplicates, field mismatches).
- Explains each issue in plain business terms and flags its likely severity.
- Ends with clear recommended next actions.
Keep it tight and practical."""


def narrate(findings):
    client, model = get_llm()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(findings, indent=2)},
        ],
    )
    return response.choices[0].message.content