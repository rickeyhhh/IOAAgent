# main.py
import re
import time
import logging
from config.config import agent
from services.history import store_history, get_history
from tool.loader import TOOLS
from entities import ChatRequest  # 导入 ChatRequest 实体类

# print(TOOLS)

def process_input(chat_request: ChatRequest):
    try:
        logging.debug(f"处理输入的实体类: {chat_request}")

        history = get_history(chat_request)
        logging.debug(f"取历史记录: {history}")

        context_lines = ["历史对话信息："]
        for record in history:
            context_lines.append(f"用户输入: {record['user_input']}\n模型回复: {record['model_output']}\n")
        context_lines.append(f"当前用户输入: {chat_request.user_query}")
        context = '\n'.join(context_lines)

        tool_codes = [item.get('tool_code') for item in chat_request.ruler_list]
        intentions = [TOOLS[tool_code].intention for tool_code in tool_codes if tool_code in TOOLS] 

        logging.debug(f"用户能使用的工具: {tool_codes}")
        logging.debug(f"能使用工具对应的意图: {intentions}")

        instruction = f"""
        请严格按照以下步骤操作：
        1. 判断当前用户输入的意图，并从下列列表[{', '.join(intentions)}]中选一项输出，请你必须返回上述列表中的选项。
        2. 请必须输出上述列表中所含的意图，格式如下：
            {{"response": ""}}
        3. 不要输出其他任何额外信息或解释。
        """
        
        result = (
            agent
            .input(context)
            .set_role("意图识别专家")
            .instruct(instruction)
            .output({"response": ""})
            .start()
        )

        logging.debug(f"Agent 结果: {result}")

        response_intention = result.get('response')
        if response_intention:
            logging.debug(f"回复意图: {response_intention}")
        else:
            logging.error("在agent回答结果中未能找到意图")
            return {"error": "未找到response字段"}
        
        temp_history = history + [{"user_input": chat_request.user_query, "model_output": response_intention}]
        for tool_code in tool_codes:
            tool = TOOLS.get(tool_code)
            if tool:
                if tool.intention in response_intention:
                    logging.debug(f"使用工具: {tool}")
                    tool.run(temp_history)
                    break
                else:
                    logging.debug("意图不匹配")
        
        store_history(chat_request, result)
        logging.debug(f"存储历史记录: {chat_request}")

        return result
    
    except Exception as e:
        logging.error(f"处理输入出错: {e}", exc_info=True)
        return {"error": str(e)}

if __name__ == "__main__":
    # # 示例 ChatRequest 实例
    # chat_request = ChatRequest(
    #     user_id="81",
    #     session_id="1",
    #     message_id="example_message",
    #     project_id="example_project",
    #     ruler_list=[
    #         {"tool_code": "device_id"},
    #     ],
    #     is_stream=False,
    #     user_query="你帮我查询一下空调id"
    # )
    
    # result = process_input(chat_request)
    # logging.debug(f"Result: {result}")







    start_time = time.time()
    chat_request = ChatRequest(
        user_id="95",
        session_id="2",
        message_id="ref_message",
        project_id="ref_project",
        ruler_list=[
            {"tool_code": "lib_web_search"},
            # {"tool_code": "device_id"},
        ],
        is_stream=False,
        user_query="星舰四飞结果如何"             #产生答案用时： 13.935162782669067 seconds
        # user_query="保安主管的职责是什么？"      #产生答案用时： 6.251716136932373 seconds
    ) 
    
    result = process_input(chat_request)
    logging.debug(f"Result: {result}")
    print("产生答案用时： %s seconds" % (time.time() - start_time))   
