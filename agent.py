import json
import os

from reconcile import load, reconcile
from llm import get_llm

DATA_DIR = "data"


def list_datasets():
    return {"datasets": [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]}


def reconcile_datasets(sales_file, warehouse_file):
    sales = load(f"{DATA_DIR}/{sales_file}")
    warehouse = load(f"{DATA_DIR}/{warehouse_file}")
    return reconcile(sales, warehouse)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_datasets",
            "description": "List the CSV datasets available for reconciliation.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reconcile_datasets",
            "description": "Compare two datasets and return the structured discrepancies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sales_file": {"type": "string", "description": "Filename of the sales export, e.g. sales_system.csv"},
                    "warehouse_file": {"type": "string", "description": "Filename of the warehouse export, e.g. warehouse.csv"},
                },
                "required": ["sales_file", "warehouse_file"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "list_datasets": list_datasets,
    "reconcile_datasets": reconcile_datasets,
}

SYSTEM_PROMPT = """You are a reconciliation agent. Use the available tools to inspect and
compare the user's datasets. Never invent transactions or numbers: rely only on what the
tools return. When you have the findings, write a concise report grouped by issue type, with
likely severity and recommended next actions."""


def run_agent(user_request, max_steps=5):
    client, model = get_llm()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_request},
    ]

    for _ in range(max_steps):
        response = client.chat.completions.create(model=model, messages=messages, tools=TOOLS)
        message = response.choices[0].message

        assistant_msg = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {"name": c.function.name, "arguments": c.function.arguments},
                }
                for c in message.tool_calls
            ]
        messages.append(assistant_msg)

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            func = TOOL_FUNCTIONS[call.function.name]
            args = json.loads(call.function.arguments)
            result = func(**args)
            print(f"[tool] {call.function.name}({args})")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })

    return "Stopped: reached the maximum number of steps without a final answer."


if __name__ == "__main__":
    request = "Reconcile the sales system export against the warehouse export and tell me what does not match."
    print(run_agent(request))