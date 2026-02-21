from fastapi import UploadFile
from langchain_anthropic import ChatAnthropic
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
# from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


from app.infrastructure.parser.execle.code import observation_callback, create_tool_callback, result_callback
from app.infrastructure.parser.execle.message import AgentStreamParser, AgentCallbacks

def ask(file:UploadFile,query:str):

    df = pd.read_excel(
            file.file
    )
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    font_path = "C:/Windows/Fonts/malgun.ttf"
    font_prop = fm.FontProperties(fname=font_path)

    plt.rcParams["font.family"] = font_prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False

    python_tool = PythonAstREPLTool()
    python_tool.locals["df"] = df


    python_tool.locals["plt"] = plt
    python_tool.locals["matplotlib"] = matplotlib

    agent = create_pandas_dataframe_agent(
        # ChatOpenAI(model="gpt-4o", temperature=0),
        ChatAnthropic(model="claude-opus-4-5-20251101",temperature=0),
        df,
        verbose=False,
        agent_type="tool-calling",
        allow_dangerous_code=True,
        prefix="You are a professional data analyst and expert in Pandas. "
        "You must use Pandas DataFrame(`df`) to answer user's request. "
        "\n\n[IMPORTANT] DO NOT create or overwrite the `df` variable in your code. \n\n"
        "If you are willing to generate visualization code, please use `plt.show()` at the end of your code. "
        "I prefer seaborn code for visualization, but you can use matplotlib as well."
        "\n\n<Visualization Preference>\n"
        "- `muted` cmap, white background, and no grid for your visualization."
        "\nRecomment to set palette parameter for seaborn plot.",
    )

    parser_callback = AgentCallbacks(create_tool_callback(python_tool=python_tool), observation_callback, result_callback)
    stream_parser = AgentStreamParser(parser_callback)

    response = agent.stream({"input": query})

    for step in response:
        stream_parser.process_agent_steps(step)

    return stream_parser.output