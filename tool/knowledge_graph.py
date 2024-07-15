from tool_base import toolbase  # 假设 toolbase 是正确的工具基类
import Agently  # 假设 Agently 是正确的引擎模块
from config.config import agent_factory

class Knowlegde_graph(toolbase):
    def __init__(self, agent):
        super().__init__(agent)
        self.description = "查询设备id"
        self.intention = "查询设备id"
        self.toolcode = "device_id"
        self.args = [
            {
                "参数名": "楼栋号",
                "中文描述": "目标设备所在的楼栋号",
                #"样例信息": "12",
                #"数据类型": "int",
            },
            {
                "参数名": "楼层数",
                "中文描述": "目标设备所在的楼层数",
                #"样例信息": "5",
                #"数据类型": "int",
            },
            {
                "参数名": "房间号",
                "中文描述": "目标设备所在的房间号",
                #"样例信息": "120501",
                #"数据类型": "int",
            }
        ]
        
    def run(self, history):
        arg_string = "; ".join(", ".join(f'{key}: {value}' for key, value in arg.items())for arg in self.args)
        workflow = Agently.Workflow()  # 假设 Agently 提供了一个 workflow 类
        tool_agent = agent_factory.create_agent()

        @workflow.chunk(
            chunk_id="Start",
            type="Start"
        )

        @workflow.chunk(
            chunk_id="args_completion",
        )
        def args_completion(self, storage):
            nonlocal history
            user_inputs = [item['user_input'] for item in history]
            print("---提取用户输入参数---" + "\n")
            print(user_inputs)
            arguments = tool_agent.input(user_inputs).instruct(f'{arg_string}这是所需要的参数，请你从历史用户对话和当前用户对话{user_inputs}提取上述参数的取值，不要自己编用户没有说的参数，用户未提到的数据项，请填None，所填参数的数据类型均为整型，请以json格式输出，不要输出其他任何额外信息或解释。').start()
            print(arguments)
            storage.set("arguments", arguments)

            indicator_1 = tool_agent.input(arguments).instruct(f'根据给你的参数，检查这些参数是否有None的项，如果有请输出Yes，如果没有请输出No，注意你只能输出Yes或No，不要输出其他任何额外信息或解释。').start()
            print(indicator_1)
            return indicator_1

        @workflow.chunk(
            chunk_id="knowledge_graph",
        )
        def knowledge_graph(self, storage):
            print("---开始填写json块---" + "\n")
            data = {
                "building number": None,
                "floor": None,
                "room number": None,
            }
            arguments = storage.get("arguments")
            json_block = tool_agent.input(data).instruct(f'根据参数 {arguments}，填写上述json块，并将填写完的json输出。不要输出其他任何额外信息或解释。').start()
            print (json_block)
            indicator_2 = tool_agent.input(json_block).instruct(f'检查上述json块中是否还有值未None的元素，如果有请输出Yes，没有则输出No').start()
            print(indicator_2)
            return json_block, indicator_2

        @workflow.chunk(
            chunk_id="quit",
        )
        def quit_executor(self, storage):
            print("---开始向用户提问补全数据---" + "\n")
            arguments = storage.get("arguments")
            question = tool_agent.input(arguments).instruct(f'{arg_string} 是全部所需的参数，{arguments} 是目前有的参数，请你向用户提问取值为None的参数').start()
            print(question)
            return question
        
        # 连接执行块
        workflow.chunks["Start"].connect_to(workflow.chunks["args_completion"])
        (
            workflow.chunks["args_completion"]
                .if_condition(lambda return_value, storage: return_value == "No").connect_to(workflow.chunks["knowledge_graph"])
                .else_condition().connect_to(workflow.chunks["quit"])
        )

        #print(workflow.draw())  # 调试输出流程图
        reply = workflow.start()
        print(reply)  # 调试输出执行结果

        return reply