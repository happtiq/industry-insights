# Copyright 2025 happtiq GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Optional

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from src.available_tool import check_product_availability
from src.search_tool import search_products

load_dotenv()


async def search_products_tool(
    query: str,
    k: int = 3,
    tool_context: Optional[ToolContext] = None,
):
    """Retrieve products from the local FAISS index and attach artifacts."""
    return await search_products(query=query, k=k)


agent = LlmAgent(
    model="gemini-2.5-pro",
    name="ConciergeAgent",
    instruction=(
        "Start by greeting the user and introducing yourself as a luxury watch and jewelry concierge for happtiq. "
        "Interpret the user's style preferences. Call search_products_tool to curate one to three pieces, "
        "then use check_product_availability when the user asks about stock levels or boutique pickup. "
        "For each product, leverage the `image_markdown` field returned by the tool to present the image (it already contains the properly formatted Markdown tag). "
        "Follow with key specs, URLs, and availability summaries as needed. "
        "Be polished, concise, and proactive about summarising availability options."
    ),
    tools=[search_products_tool, check_product_availability],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=5000,
    ),
)
