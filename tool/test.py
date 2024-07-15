from tool_base import toolbase  # 假设 toolbase 是正确的工具基类
import Agently  # 假设 Agently 是正确的引擎模块

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

        @workflow.chunk(
            chunk_id="Start",
            type="Start"
        )

        @workflow.chunk(
            chunk_id="args_completion",
        )
        def args_completion(self, storage):
            nonlocal history
            print("---提取用户输入参数---" + "\n")
            print(history)
            arguments = agent.input(history).instruct(f'{arg_string}这是所需要的参数，请你根据用户的对话{history}提取上述参数的取值，不要提取用户没有提到的参数。').start()
           
            print(arguments)
            storage.set("arguments", arguments)
            indicator = agent.input(arguments).instruct(f'根据给你的参数，判断这些参数有没有包含 {arg_string} 中所有的参数，如果有请你输出Yes，如果没有请你输出No').start()
            print(indicator)
            return indicator

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
            json_block = agent.input(data).instruct(f'根据参数 {arguments}，填写上述json块，并将填写完的json输出。').start()
            print (json_block)
            return json_block

        @workflow.chunk(
            chunk_id="quit",
        )
        def quit_executor(self, storage):
            print("---开始向用户提问补全数据---" + "\n")
            arguments = storage.get("arguments")
            question = agent.input(arguments).instruct(f'{arg_string} 是全部所需的参数，{arguments} 是目前有的参数，请你向用户提问目前还确少的参数。').start()
            print(question)
            return question
        
        # 连接执行块
        workflow.chunks["Start"].connect_to(workflow.chunks["args_completion"])
        (
            workflow.chunks["args_completion"]
                .if_condition(lambda return_value, storage: return_value == "Yes").connect_to(workflow.chunks["knowledge_graph"])
                .else_condition().connect_to(workflow.chunks["quit"])
        )

        #print(workflow.draw())  # 调试输出流程图
        reply = workflow.start()
        print(reply)  # 调试输出执行结果

        return reply

if __name__ == "__main__":
    # 示例使用 Knowlegde_graph 类
    agent_factory = (
    Agently.AgentFactory()
        .set_settings("current_model", "OAIClient")
        .set_settings("model.OAIClient.auth.api_key", "nothing")  # 如果不需要 API key，可以为空
        #.set_settings("model.OAIClient.options", {"model": "kagentlms_baichuan2_13b_mat"})  # 设置您的模型标识
        .set_settings("model.OAIClient.options", {"model": "qwen1.5_14b"})  # 设置您的模型标识
        .set_settings("model.OAIClient.url", "http://localhost:8888/v1")  # 您本地模型的URL
)

    agent = agent_factory.create_agent()

    knowledge_graph_tool = Knowlegde_graph(agent)
    history = "帮我查下1号楼12层1201房的空调的id"  # 假设这里提供了适当的历史记录对象
    # 调用 run 方法执行工具流程
    
    result = knowledge_graph_tool.run(history)
