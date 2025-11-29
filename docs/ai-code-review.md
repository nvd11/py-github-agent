我需要实现一个github pr的ai code review的功能
用于被另一个webhook svc调用


要求:

1. 接受 pull request url 的参数
2. 输出 ai code review的j结果

输出json格式为

{
    fidnings:[

        {
            filename,
            line number,
            issue,
            suggestion
        }
        .........

    ]
}

3.利用github agent实现 , src/agents/github_agent.py
4.扩展github toolf的能力, 能获取一个pr中对于code review所有需要的信息

信息的格式是

{
    changed_files{
        filename(withfilepath),
        stauts,(added,modified,deleted)
        original_content,
        updated_content
        diff_info
    }
}

5.获取一个pr中对于code review所有需要的信息 ->具体的实现在github_service.里实现( 已经实现 - GitHubService.get_pr_code_review_info)
6.获得 pr info后, 调用llm获得review输出
7.agent输出的格式是一个md的格式, 包含pr的changed summary, 和一个table的格式, columns 就是filename, linenumber, issue, suggestion


8.写一个pytest case 调用github agent

帮我编写一个开发计划文档, 包括流程图, 要开发的python 类or文件list出来



