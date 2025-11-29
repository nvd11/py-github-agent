import pytest
from src.services.github_service import GitHubService
from loguru import logger

@pytest.mark.asyncio
async def test_get_pull_requests():
    """
    Tests the get_pull_requests method of the GitHubService.
    """
    logger.info("Testing GitHubService.get_pull_requests...")
    service = GitHubService()
    owner = "nvd11"
    repo = "py-github-agent"
    
    try:
        # We know from previous checks there are closed PRs, so we test with state="all"
        prs = await service.get_pull_requests(owner, repo, state="all")
        
        assert prs is not None
        assert isinstance(prs, list)
        assert len(prs) > 0
        
        # Check if a known PR number is in the results
        pr_numbers = {pr['number'] for pr in prs}
        assert 1 in pr_numbers
        assert 2 in pr_numbers
        
        logger.success(f"get_pull_requests returned {len(prs)} pull requests.")
        print(f"Found PR #2: {[pr for pr in prs if pr['number'] == 2][0]['title']}")

    except Exception as e:
        pytest.fail(f"get_pull_requests failed with an exception: {e}")

@pytest.mark.asyncio
async def test_get_all_files_list():
    """
    Tests the get_all_files_list method of the GitHubService.
    """
    logger.info("Testing GitHubService.get_all_files_list...")
    service = GitHubService()
    owner = "nvd11"
    repo = "py-github-agent"
    
    try:
        files = await service.get_all_files_list(owner, repo, branch="main")
        
        assert files is not None
        assert isinstance(files, list)
        assert len(files) > 0
        
        # Check if some known files are in the list
        assert "README.md" in files
        assert "Dockerfile" in files # 检查一个远程仓库中确定存在的文件
        
        logger.success("get_all_files_list returned a valid list of files.")
        print(f"Found {len(files)} files. First 5:")
        for f in files[:5]:
            print(f"  - {f}")

    except Exception as e:
        pytest.fail(f"get_all_files_list failed with an exception: {e}")
