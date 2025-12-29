# ML105: Agentic AI

This is a mini crash course on Agentic AI to set up the foundational knowledge in the field. Find the video recording on youtube.

Agent pseudocode:

```
while True:
    user query = get_user_input()
    response = invoke_llm(user_query)

    while response.has_tool_call():
        tool_result = invoke_tool(response.tool_spec)
        memory = append_context()
        response = invoke_llm(tool_output, memory)

    final_answer = response
    return final_answer
```



Author: Rola Dali
