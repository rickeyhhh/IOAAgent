from tools.tool_base import toolbase
import Agently

class Knowlegde_graph(toolbase):
    def __init__(self, agent):
        super().__init__(agent)
        self.description = "查询设备id"
        self.intention = "查询设备id"
        self.toolcode = "device_id"
        self.args = [{
            "参数名":"楼栋号",
            "中文描述":"目标设备所在的楼栋号",
            "样例信息":"12",
            "数据类型":"int",
                    },
            {       
            "参数名":"楼层数",
            "中文描述":"目标设备所在的楼层数",
            "样例信息":"5",
            "数据类型":"int",
                    },
            {       
            "参数名":"房间号",
            "中文描述":"目标设备所在的房间号",
            "样例信息":"120501",
            "数据类型":"int",
                    }]
        
    def run(self, history):
        arg_string = "; ".join(", ".join(f'{key}: {value}' for key, value in self.args.items())for arg in self.args)
        workflow = Agently.workflow()

        @workflow.chunk(
            chunk_id = "Start",
            type = "Start"
        )

        @workflow.chunk(
            chunk_id = "args_completion"
            
        )
        def indicator(self, history):
            arguments = self.agent.input(history).instruct(f'从给你的历史输入中，提取出以下参数:{arg_string},不要提取用户没有提到的参数。').start()
            indicator = self.agent.input(arguments).instruct(f'根据给你的参数，判断这些参数有没有包含{arg_string}中所有的参数，如果有请你输出Yes，如果没有请你输出No').start()

        @workflow.chunk(
            chunk_id = "knowledge_graph",
        )
        def knowledge_graph(self, arguments):
            #填写json块，向图谱查询设备id
            data = {
                "building number": None,
                "floor": None,
                "room number": None,
            }
            json_block = self.agent.input(data).instruct(f'根据参数{arguments}，填写上述json块，并将填写完的json输出。')
            return(json_block)
        
        @workflow.chunk(
            chunk_id = "quit",
        )
        def quit_executor(self, history, arguments):
            question = self.agent.input(arguments).instruct(f'{arg_string}是全部所需的参数，{arguments}是目前有的参数，请你提问目前还确少的参数。').start()
            return(question)
        
        #连接执行块
        workflow.chunks["Start"].connect_to(workflow.chunks["args_completion"])
        (
            workflow.chunks["args_completion"]
                .if_condition(indicator == "Yes").connect_to(workflow.chunks["knowledge_graph"])
                .else_condition().connect_to(workflow.chunks["quit"])
        )

        print(workflow.draw())
        workflow.start()