
import src.configs.config
from loguru import logger

import os
import aiohttp
from loguru import logger
from typing import List, Dict, Any



class GitHubService:
    """
    一个用于与 GitHub API 交互的服务类。
    """
    BASE_URL = "https://api.github.com"

    def __init__(self,_token: str = os.getenv("GITHUB_TOKEN")):
        self.token = _token
        if not self.token:
            logger.warning("GITHUB_TOKEN not found in environment variables. API requests will be unauthenticated and subject to lower rate limits.")
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def get_pull_requests(
        self, repo_owner: str, repo_name: str, state: str = "open"
    ) -> List[Dict[str, Any]]:
        """
        异步获取指定 GitHub 仓库的 Pull Request 列表。

        :param repo_owner: 仓库所有者
        :param repo_name: 仓库名称
        :param state: PR 的状态 ('open', 'closed', 'all')
        :return: 一个包含 PR 关键信息的字典列表
        """
        url = f"{self.BASE_URL}/repos/{repo_owner}/{repo_name}/pulls"
        params = {"state": state}
        logger.info(f"Fetching pull requests from {url} with state: {state}")

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()  # 如果状态码是 4xx 或 5xx，则抛出异常
                    pulls_data = await response.json()
            
            # 提取关键信息
            simplified_pulls = [
                {
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "state": pr.get("state"),
                    "url": pr.get("html_url"),
                    "user": pr.get("user", {}).get("login"),
                }
                for pr in pulls_data
            ]
            logger.success(f"Successfully fetched {len(simplified_pulls)} pull requests.")
            return simplified_pulls

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching pull requests for {repo_owner}/{repo_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return []

    async def get_all_files_list(self, repo_owner: str, repo_name: str, branch: str = "main") -> List[str]:
        """
        异步获取指定 GitHub 仓库分支中所有文件的完整路径列表。
        """
        url = f"{self.BASE_URL}/repos/{repo_owner}/{repo_name}/git/trees/{branch}?recursive=1"
        logger.info(f"Fetching file list for {repo_owner}/{repo_name} on branch {branch}")

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    tree_data = await response.json()
            
            if tree_data.get("truncated"):
                logger.warning(f"File list for {repo_owner}/{repo_name} is truncated because it exceeds the API limit.")

            if "tree" not in tree_data:
                logger.error("API response does not contain a 'tree' field.")
                return []

            file_paths = [item["path"] for item in tree_data["tree"] if item.get("type") == "blob"]
            logger.success(f"Successfully fetched {len(file_paths)} file paths.")
            return file_paths

        except aiohttp.ClientError as e:
            logger.error(f"Error fetching file list for {repo_owner}/{repo_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return []








    async def _fetch_file_content(self, session: aiohttp.ClientSession, repo_owner: str, repo_name: str, path: str, ref: str) -> str:
        """
        Helper to fetch raw file content from GitHub API.
        """
        url = f"{self.BASE_URL}/repos/{repo_owner}/{repo_name}/contents/{path}"
        params = {"ref": ref}
        # Create a new headers dict for this request to include the raw accept header
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.raw"
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 404:
                    logger.warning(f"File {path} not found at ref {ref} (possibly deleted or new)")
                    return ""
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f"Failed to fetch content for {path} at {ref}: {e}")
            return ""
        



        
    async def get_pr_code_review_info(self, repo_owner: str, repo_name: str, pull_number: int) -> Dict[str, Any]:
        """
        获取 PR 的 Code Review 所需的所有信息：
        包括变更的文件列表、Diff、以及每个文件的原始内容和修改后内容。
        """
        import asyncio
        
        logger.info(f"Fetching PR info for {repo_owner}/{repo_name}#{pull_number}")
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # 1. Get PR details to find base and head SHA
                pr_url = f"{self.BASE_URL}/repos/{repo_owner}/{repo_name}/pulls/{pull_number}"
                async with session.get(pr_url) as response:
                    response.raise_for_status()
                    pr_data = await response.json()
                
                base_sha = pr_data["base"]["sha"]
                head_sha = pr_data["head"]["sha"]
                
                # 2. Get list of changed files
                files_url = f"{self.BASE_URL}/repos/{repo_owner}/{repo_name}/pulls/{pull_number}/files"
                async with session.get(files_url) as response:
                    response.raise_for_status()
                    files_data = await response.json()
                
                logger.info(f"Found {len(files_data)} changed files. Fetching contents...")
                
                # 3. Concurrently fetch content for all files
                tasks = []
                for file_info in files_data:
                    filename = file_info["filename"]
                    status = file_info["status"]
                    
                    # Fetch original content (from base)
                    if status == "added":
                        original_task = asyncio.create_task(asyncio.sleep(0, result="")) # No original content
                    else:
                        original_task = self._fetch_file_content(session, repo_owner, repo_name, filename, base_sha)
                        
                    # Fetch updated content (from head)
                    if status == "removed":
                        updated_task = asyncio.create_task(asyncio.sleep(0, result="")) # No updated content
                    else:
                        updated_task = self._fetch_file_content(session, repo_owner, repo_name, filename, head_sha)
                        
                    tasks.append((file_info, original_task, updated_task))
                
                results = []
                for file_info, original_task, updated_task in tasks:
                    original_content = await original_task
                    updated_content = await updated_task
                    
                    results.append({
                        "filename": file_info["filename"],
                        "status": file_info["status"],
                        "diff_info": file_info.get("patch", ""),
                        "original_content": original_content,
                        "updated_content": updated_content
                    })
                
                return {"changed_files": results}

        except Exception as e:
            logger.error(f"Error getting PR code review info: {e}")
            return {"changed_files": []}
