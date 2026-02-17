from langchain_experimental.tools import PythonAstREPLTool

# 파이썬 코드를 실행하는 도구를 생성합니다.
# python_tool = PythonAstREPLTool()
# python_tool.locals["df"] = df


def create_tool_callback(python_tool):

    def tool_callback(tool) -> None:
        print("<<<<<<< Code >>>>>>")

        if tool_name := tool.get("tool"):
            if tool_name == "python_repl_ast":
                tool_input = tool.get("tool_input")
                for k, v in tool_input.items():
                    if k == "query":
                        print(v)
                        result = python_tool.invoke({"query": v})
                        print(result)

        print("<<<<<<< Code >>>>>>")

    return tool_callback


# 관찰 결과를 출력하는 콜백 함수입니다.
def observation_callback(observation) -> None:
    print(f"<<<<<<< Message >>>>>>")
    if "observation" in observation:
        print(observation["observation"])
    print(f"<<<<<<< Message >>>>>>")


# 최종 결과를 출력하는 콜백 함수입니다.
def result_callback(result: str) -> None:
    print(f"<<<<<<< 최종 답변 >>>>>>")
    print(result)
    print(f"<<<<<<< 최종 답변 >>>>>>")