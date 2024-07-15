import Agently
import os
import sys


# print(sys.path)
# utils_path = '/home/langchao/IOAAgentApi/utils'  # 替换为utils包的实际路径
# if utils_path not in sys.path:
#     sys.path.append(utils_path)
# print(sys.path)

utils_path = '/home/langchao/IOAAgentApi/utils'  # 替换为utils包的实际路径
if utils_path not in sys.path:
    sys.path.append(utils_path)

from WebGLM.model import load_model, citation_correction
from WebGLM.arguments import add_model_config_args
from sentence_transformers import SentenceTransformer
import argparse
from time import time

from tool_base import toolbase


class LibWebSearch(toolbase):
    def __init__(self, agent=None, top_k=10):
        super().__init__(agent)
        self.description = "获取回答问题所需的知识"
        self.intention = "外部知识" #参考信息
        self.toolcode = "lib_web_search"
        #知识库检索和外部检索应该不需要参数补全，只需要一个query即可
        self.top_k = top_k
        self.embedding_model = SentenceTransformer('/home/langchao/IOAAgentApi/utils/WebGLM/MokaAI/m3e-base')
        self.COLLECTION_NAME = "WuYeKnowledgeLib"


    # def run(self, history, query):
    #     result = self.agent.input(history).instruct(f'找出能够回答这个问题的参考信息:{query}').start()
    def run(self, query=None, history=None):
        workflow = Agently.Workflow()
        @workflow.chunk()
        def retrieve_from_lib(self, inputs, storage):    #向量检索
            top_k = self.top_k
            client = MilvusClient(
                uri="http://localhost:19530"
            )
            query_vectors = self.embedding_model.encode([query])
            try:
                res = client.search(
                    collection_name=self.COLLECTION_NAME,     # target collection
                    data=query_vectors,                # query vectors
                    limit=top_k,                           # number of returned entities
                    output_fields=["content", "content_id", "file_name", "file_id", "project_id"]
                )
            except Exception as e:
                print("Error: " + str(e))
                return str(e), 500

            res1 = [item['entity']['content'] for sublist in res for item in sublist]
            retrieve_result = '\n'.join(res1)

            return retrieve_result
        
        @workflow.chunk()
        def decide_if_websearch(self, inputs, storage):  #判断检索出来的内容是否已经足够作为参考信息
            lib_ref = inputs["default"]
            # if_search = self.agent.input(history).instruct(f'现在有一个问题:{query}\n以及它的参考信息:\n{lib_ref}\n请判断\
            # 参考信息是否足够回答问题，如果足够，请回答1；否则回答0。').start()
            
            # tokenizer = AutoTokenizer.from_pretrained(webglm_ckpt_path, trust_remote_code=True)
            # model = AutoModel.from_pretrained(webglm_ckpt_path, trust_remote_code=True, device='cuda')
            # model.to(device)
            # model.eval()        
            prompt = f'现在有一个问题:{query}\n以及它的参考信息:\n{lib_ref}\n请判断\
            # 参考信息是否足够回答问题，如果足够，请回答1；否则回答0。'
           
            start_time = time.time()
            outputs, history = self.agent.input(history).instruct(prompt).start()
            print({"answer": outputs})
            print("产生答案用时： %s seconds" % (time.time() - start_time))
            if_search = outputs

            return if_search
            
        @workflow.chunk()
        def retrieve_from_web(self, inputs, storage):
            arg = argparse.ArgumentParser()
            add_model_config_args(arg)
            args = arg.parse_args()
            webglm = load_model(embedding_model, args)
            question = query
            start_time = time()  #测试时间
            question = question.strip()
            final_results = {}
            output = webglm.stream_query(question)

            print("Time taken: %.2f seconds"%(time() - start_time))
            references = [ref['text'] for ref in output]
            references = '\n'.join(references)
            return references

        @workflow.chunk()
        def conclude(self, inputs, storage):
            return inputs["default"]

        (
            workflow
                .connect_to("retrieve_from_lib")
                .connect_to("decide_if_websearch")
                .if_condition(lambda return_value, storage: return_value > 0)
                    .connect_to("conclude")
                .else_condition()
                    .connect_to("retrieve_from_web")
                    .connect_to("conclude")
        )

        workflow.chunks["conclude"].connect_to("END")
        # result = result = workflow.start(
        #     "Hello Agently", 
        #     storage={ "init_storage": "Hello Agently Workflow" }
        # )
        result = workflow.start()
        print("tool输出为：", result)

if __name__ == "__main__":
    search_workflow = LibWebSearch()
    search_workflow.run(query="会所经营助理的职权有哪些？")

    '''
    python -m fastchat.serve.controller
    python -m fastchat.serve.vllm_worker --model-path /home/langchao/projects_jzh/KwaiAgents/kwaiagents/pretrained_models/qwen1.5_14b_mat/qwen1.5_14b --trust-remote-code --num-gpus 2 --gpu-memory-utilization 0.95 --max-model-len 4096
    '''