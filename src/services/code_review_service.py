import re
from loguru import logger
from src.agents.code_review_agent import create_code_review_agent
from langchain_core.runnables import Runnable

class CodeReviewService:
    def __init__(self, agent_executor: Runnable):
        self.agent_executor = agent_executor

    @classmethod
    def parse_pr_url(cls, url: str) -> dict:
        """
        Parses a GitHub PR URL to extract owner, repo, and pull_number.
        Format: https://github.com/{owner}/{repo}/pull/{number}
        """
        pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.search(pattern, url)
        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {url}")
        
        return {
            "repo_owner": match.group(1),
            "repo_name": match.group(2),
            "pull_number": int(match.group(3))
        }

    async def perform_code_review(self, pr_url: str) -> str:
        """
        Orchestrates the code review process.
        """
        logger.info(f"Starting code review for PR: {pr_url}")
        
        # 1. Validate URL
        try:
            pr_info = self.parse_pr_url(pr_url)
            logger.info(f"Parsed PR info: {pr_info}")
        except ValueError as e:
            logger.error(f"URL parsing error: {e}")
            return f"Error: {str(e)}"

        # 2. Construct Prompt for Agent
        # Note: Our agent is smart enough to extract info from the prompt if we format it naturally,
        # OR we can pass structured input if we change the agent interface.
        # Since our agent currently takes a string input via `arun`, we construct a clear instruction.
        input_text = (
            f"Please review pull request #{pr_info['pull_number']} "
            f"in repository {pr_info['repo_owner']}/{pr_info['repo_name']}."
        )
        
        # 3. Call Agent
        try:
            # Use correct message format for new agent architecture
            from langchain_core.messages import HumanMessage
            result = await self.agent_executor.ainvoke({
                "messages": [HumanMessage(content=input_text)]
            })
            
            # Extract output from messages
            messages = result.get("messages", [])
            if messages:
                # Get the last AI message content
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    # If content is a list, extract text part
                    if isinstance(last_message.content, list) and len(last_message.content) > 0:
                        # Extract first text block content
                        output = last_message.content[0].get('text', '') if isinstance(last_message.content[0], dict) else str(last_message.content[0])
                    else:
                        output = str(last_message.content)
                else:
                    output = str(last_message)
            else:
                output = ""
            
            if not output:
                # Log the full result for debugging purposes
                logger.error(f"Agent returned empty output. Full result object: {result}")
                return f"Error: Agent returned empty response. Internal result state: {result}"
                
            return output

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return f"An error occurred during code review: {str(e)}"
