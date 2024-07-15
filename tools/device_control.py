from datetime import datetime
from knowledge_graph import knowledge_graph
from device_info import query_device_info
from config.config import agent_factory
import Agently

device_info = {
    "building number": {
        "value": None,
    },
    "floor": {
        "value": None,
    },
}

def start(*, agent_factory, SETTINGS, root_path, logger, user_input):
    main_workflow = Agently.Workflow()

    # Define Workflow Chunks
    @main_workflow.chunk("start", type="Start")

    @main_workflow.chunk("user_request")
    def request_executor(inputs, storage):
        storage.set(
            "user_request",
            user_input,
        )

    @main_workflow.chunk("information_json_completion")
    def information_json_completion(inputs, storage):
        device_info = storage.get("instruction_json")
        agent = agent_factory.create_agent()
        # Prepare Basic Information for Agent
        agent\
            .set_role("Role", "JSON block completino Expert")\
            .general(
                "Current Date",
                datetime.now().date()
            )
        # Start the Survey
        can_stop = False
        chat_history = []
        # Update logic to suit some models require chat history strictly follow the
        # order: user-assistant-user-assistant
        # This logic down below works perfect for OpenAI GPT
        '''
        chat_history.append({ "role": "assistant", "content": opening["opening"] })
        '''
        while not can_stop:
            # Planning: Check Survey Form and Ask Question
            question_plan = agent\
                .chat_history(chat_history)\
                .instruct(
                    "Action Rules",
                    [
                        "1. Check {device_info} form and make sure all filled items have complete and correct information.",
                        "2. If there're incomplete or incorrect information, choose one of the items and asking user again.",
                        "3. If there're still blank items, choose one of the blank items to ask.",
                        "4. Do remember to check chat history and do not repeat questions that are already asked and responsed correctly.",
                    ]
                )\
                .input({
                    "device_info": device_info,
                })\
                .output({
                    "incorrect_items": ("Array | Null", "list items names with incorrect information."),
                    "target_item": ("String", "choose one target item for this question round. If there're incorrect items, ask them first."),
                    "question": ("String", "your question about {target_item} to user. Check chat history, don't repeat yourself."),
                })\
                .start()
            # Asking: Survey Agent Interact with user
            print("[Completion Agent]: ", question_plan["question"])
            need_to_dig_deep = True
            while need_to_dig_deep:
                user_response = input(f"[User]:  ")
                # Filling the Form: Completion Agent Analyses the Response, Fills the Form and Replies.
                analysis = agent\
                    .chat_history(chat_history)\
                    .input({
                        "question_target_item": question_plan["target_item"],
                        "question": question_plan["question"],
                        "user_response": user_response,
                    })\
                    .info({ "device_info": device_info })\
                    .instruct("Using the language user prefer especially when user asked clearly!!!")\
                    .output({
                        "fillings": [{
                            "target_item": ("String", "according {user_response}, which item from {device_info} is response about?"),
                            "value": ("As required", "value you will fill into the form about {target_item} according {device_info} required"),
                            # "userr_explation": ("String | Null", "Extra explation from the customer"),
                        }],
                        "need_to_dig_deep": ("Boolean", "if {user_response} is not so exactly and according chat history you think you can get more information, return true"),
                        "reply": "Your reply to user, to finish this item's question-answer or question to dig deep",
                    })\
                    .start()
                need_to_dig_deep = analysis["need_to_dig_deep"] if "need_to_dig_deep" in analysis else False
                if "fillings" in analysis:
                    for filling in analysis["fillings"]:
                        if filling["target_item"] not in device_info:
                            device_info.update(filling["target_item"], {})
                        device_info[filling["target_item"]]["value"] = filling["value"]
                        if "user_explation" in filling\
                            and filling["customer_explation"] not in (None, ""):
                            device_info[filling["target_item"]]["customer_explation"]\
                                .append(str(filling["user_explation"]))
                print("[Completion Agent]: ", analysis["reply"])
                # Update logic to suit some models require chat history strictly follow the
                # order: user-assistant-user-assistant
                chat_history[-1]["content"] += "\n" + question_plan["question"]
                chat_history.extend([
                    { "role": "user", "content": user_response },
                    { "role": "assistant", "content": analysis["reply"] }
                ])
                # This logic down below works perfect for OpenAI GPT
                '''
                chat_history.extend([
                    { "role": "assistant", "content": question_plan["question"] },
                    { "role": "user", "content": customer_response },
                    { "role": "assistant", "content": analysis["reply"] }
                ])
                '''
            # Can Stop Check
            can_stop_judgement = agent\
                .info({
                    "device_info": device_info
                })\
                .output({
                    "can_stop_judgement": (
                        "Boolean",
                        "if all device_info required items are filled " + \
                        "you can stop."
                    ),
                    "stop_reply": ("String", "if {hang_up_judgement} is true, generate your thanks and goodbye reply"),
                })\
                .start()
            if can_stop_judgement["can_stop_judgement"]:
                can_stop = True
                print("[Survey Agent]: ", can_stop_judgement["stop_reply"])
                chat_history[-1]["content"] += "\n" + can_stop_judgement["stop_reply"]
                #chat_history.append({ "role": "assistant", "content": can_stop_judgement["stop_reply"]})
                print("[Completion Form]:\n", device_info)
        
        storage.set(
            "information_json",
            device_info,
        )

    @main_workflow.chunk("retrieve_device_id")
    def retrieve_device_id(inputs, storage):
        json_data = storage.get("json_data")
        device_id = knowledge_graph(json_data)
        storage.set(
            "device_id",
            device_id,
        )
        

    @main_workflow.chunk("retrieve_device_info")
    def retrieve_device_info(inputs, storage):
        device_id = storage.get("device_id")
        instruction_data = query_device_info(device_id)
        storage.set(
            "instruction_data",
            instruction_data,
        )

    @main_workflow.chunk("instruction_json_completion")    
    def instruction_json_completion(inputs, storage):
        instruction_data = storage.get("instruction_data")
        agent = agent_factory.create_agent()
        # Prepare Basic Information for Agent
        # # Filling the Form: Completion Agent Analyses the Response, Fills the Form and Replies.
        agent\
            .set_role("Role", "JSON block completion Expert")\
            .input(user_input)\
            .info({ "instruction_data": instruction_data})\
            .instruct("Using the language user prefer especially when user asked clearly!!!")\
            .start()    
        
        storage.set(
                "instruction_json",
                instruction_data,
            )

    @main_workflow.chunk("device_control")
    def device_control(inputs, storage):
        

    # Connect Chunks
    (
        main_workflow.chunks["start"]
            .connect_to(main_workflow.chunks["user_request"])
            .connect_to(main_workflow.chunks["information_json_completion"])
            .connect_to(main_workflow.chunks["retrieve_device_id"])
            .connect_to(main_workflow.chunks["retrieve_device_info"])
            .connect_to(main_workflow.chunks["instruction_json_completion"])
            .connect_to(main_workflow.chunks["device_control"])
    )

    # Start Workflow
    main_workflow.start()

tool_info = {
    "tool_name": "device_control",
    "desc": "Control devices based on user's instruction.",
    "args": {
        "user_input": (
            "str",
            "[*Required] The original input of user."
        )
    },
    "func": start
}

Agently.global_tool_manager.register(**tool_info)