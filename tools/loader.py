# tools/loader.py
import os
import sys
import importlib


sys.path.append(os.path.dirname(os.path.abspath(__file__)))# 将当前路径添加到 sys.path, 保证import正确

def load_tools():
    tools = {}
    tool_dir = os.path.dirname(__file__)
    for file in os.listdir(tool_dir):
        if file.endswith('.py') and file not in ['tool_base.py', 'loader.py', '__init__.py']:
            module_name = f'{file[:-3]}'
            try:
                module = importlib.import_module(module_name)
                for attr in dir(module):
                    tool_class = getattr(module, attr)
                    if isinstance(tool_class, type):
                        try:
                            tool_instance = tool_class(None)  # Ensure `None` is an acceptable argument for agent
                            if hasattr(tool_instance, 'toolcode'):
                                tools[tool_instance.toolcode] = tool_instance.intention
                        except Exception as e:
                            print(f"Error loading {module_name}.{attr}: {e}")
            except Exception as e:
                print(f"Error importing module {module_name}: {e}")
    return tools

TOOLS = load_tools()

if __name__ == "__main__":
    print(TOOLS)
