from tools.tool_base import toolbase

class Device_State(toolbase):
    def __init__(self, agent):
        super().__init__(agent)
        self.description = "查询设备状态"
        self.intention = "设备状态"
        self.toolcode = "device_state"
        self.args = [{
            "参数名":"",
            "中文描述":"",
            "样例信息":"",
            "数据类型":"",
                    },
            {       
            "参数名":"",
            "中文描述":"",
            "样例信息":"",
            "数据类型":"",
                    }]
        

    def run(self, history):
        arg_string = "; ".join(", ".join(f'{key}: {value}' for key, value in self.args.items())for arg in self.args)
        result = self.agent.input(history).instruct(f'提取出以下参数:{arg_string}').start()
        print(result)
