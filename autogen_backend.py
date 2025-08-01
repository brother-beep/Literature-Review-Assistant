from __future__ import annotations
import asyncio
from typing import AsyncGenerator, Dict, List
import arxiv
import markdown

import os
from datetime import datetime
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create export folder if needed
EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# 1. Tool definition
def arxiv_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Return a compact list of arxiv papers matching *query*
    Each element contains: 'title', 'authors', 'published', 'summary' and 'pdf_url'.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers: List[Dict] = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "published": result.published.strftime("%Y-%m-%d"),
            "summary": result.summary,
            "pdf_url": result.pdf_url,
        })
    return papers

arxiv_tool = FunctionTool(
    arxiv_search,
    description=(
        "Search arXiv and return up to *max_results* papers, each containing "
        "title, authors, publication date, abstract, and pdf_url."
    ),
)

# 2. Agent team
def build_team(model: str = "gemini-2.5-flash") -> RoundRobinGroupChat:
    """Create and return a two-agent RoundRobinGroupChat team."""
    llm_client = OpenAIChatCompletionClient(model=model, api_key="AIzaSyCSE1aNfEjmiPXoEzIuWtNJiVgwwcg1180")

    search_agent = AssistantAgent(
        name="search_agent",
        description="Crafts arXiv queries and retrieves candidate papers.",
        system_message="""
        Given a user topic, think of the best arXiv query and call the
        provided tool. Always fetch five-times the papers requested so that you can
        down-select the most relevant ones. When the tool returns, choose exactly the number
        of papers requested and pass them as concise JSON to the summarizer.
        """,
        tools=[arxiv_tool],
        model_client=llm_client,
        reflect_on_tool_use=True,
    )

    summarizer = AssistantAgent(
        name="summarizer",
        description="Produce a short Markdown review from provided papers.",
        system_message="""
        You are an expert researcher writing literature reviews in Markdown format.

        When given a JSON list of papers, generate a clean, structured Markdown report:

        1. Start with a 2-3 sentence introduction summarizing the research theme or domain.
        2. Then, for each paper, include a well-formatted bullet with:
            - Title (as a Markdown link using the `pdf_url`)
            - Authors
            - Publication date
            - Abstract
            - Specific problem addressed
            - Key contributions or results

        Use the following format:

        ### 📚 Literature Review on <Insert Topic>

        <Brief introduction>

        #### 🔍 Reviewed Papers

        - **[Title](pdf_url)**
          - **Authors:** A, B, C
          - **Published:** YYYY-MM-DD
          - **Abstract:** ...
          - **Problem:** ...
          - **Contributions:** ...

        #### ✅ Summary Takeaway
        <1-sentence conclusion>

        All responses must be in valid Markdown.
        """,
        model_client=llm_client,
    )

    return RoundRobinGroupChat(
        participants=[search_agent, summarizer],
        max_turns=2,
    )

# 3. Orchestrator
async def run_litrev(
    topic: str,
    num_papers: int = 5,
    model: str = "gemini-2.5-flash",
    export_pdf: bool = True,
) -> AsyncGenerator[str, None]:
    """
    Stream structured Markdown output from the summarizer agent only.
    Also saves the Markdown and optionally exports to PDF.
    """
    team = build_team(model=model)
    task_prompt = (
        f"Conduct a literature review on **{topic}** and return exactly {num_papers} papers."
    )

    markdown_output = ""
    async for msg in team.run_stream(task=task_prompt):
        if isinstance(msg, TextMessage) and msg.source == "summarizer":
            markdown_output += msg.content + "\n"

    final_output = markdown_output.strip()

    # Save to Markdown file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{EXPORT_DIR}/litreview_{timestamp}"
    md_path = f"{base_filename}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_output)

    yield final_output

# 4. CLI testing
if __name__ == "__main__":
    async def _demo() -> None:
        async for markdown in run_litrev("Enter your search query..", num_papers=4):
            print(markdown)

    asyncio.run(_demo())
