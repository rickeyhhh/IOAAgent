import os
import sys
import importlib
import logging
# from config.logging_config import *
# logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # 将当前路径添加到 sys.path, 保证import正确

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def load_tools():
    tools = {}
    tool_dir = os.path.dirname(__file__)
    for file in os.listdir(tool_dir):
        if file.endswith('.py') and file not in ['tool_base.py', 'loader.py', '__init__.py']:
            module_name = f'{file[:-3]}'
            try:
                # print("module names: ", module_name)
                module = importlib.import_module(module_name)
                # print("module names: ", module_name)

                logging.debug(f"成功导入模块： {module_name}")
                for attr in dir(module):
                    # print(attr)
                    tool_class = getattr(module, attr)
                    if isinstance(tool_class, type):
                        try:
                            # if attr == "MilvusClient"
                            tool_instance = tool_class(None)
                            if hasattr(tool_instance, 'toolcode'):
                                # print("tool_instance.toolcode:                   ",tool_instance.toolcode)
                                tools[tool_instance.toolcode] = tool_instance
                                logging.debug(f"从模块：{module_name}.{attr}成功注册工具： {tool_instance.toolcode}")
                        except Exception as e:
                            logging.error(f"注册工具出错： {module_name}.{attr}: {e}", exc_info=True)
            except Exception as e:
                logging.error(f"导入模块错误： {module_name}: {e}", exc_info=True)
    return tools

TOOLS = load_tools()




if __name__ == "__main__":
    print(TOOLS)
    