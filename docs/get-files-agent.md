帮我用langchain的agent框架帮我写一个github ai-agent


里面包含以下功能
1.根据用户的自然语言指令, 调用github-api github仓库中list某个repo的所有文件列表
2.之后的功能以后补充

要求
1.这个agent 调用src/services/github_service.py 里的 get_all_files_list 方法
2. 编写一个pytest 来测试这个agent
3. pytest case 调用 llm_srvice的ainvoke()作为自然语言的入口, 输出的内容要有github repo的file list




切换deepseek
参考src/llm/custom_gemini.py 
帮我编写另一个llmmodel实现, 基于deekseek, apikey在.env里有

在config_<env>.yaml中添加一个option项, 选择系统使用哪一个model


对于 test_llm_service_astream
为何我切换使用gemini时 , 输出是一次性输出到console的? 并没有streaming output的打字机效果?

而使用deepseek时是正常的