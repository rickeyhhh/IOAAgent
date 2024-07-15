from tool_base import toolbase  # 假设 toolbase 是正确的工具基类
import Agently  # 假设 Agently 是正确的引擎模块
from config.config import agent_factory
import os
import sys


utils_path = '/home/langchao/IOAAgentApi/utils'  # 替换为utils包的实际路径
if utils_path not in sys.path:
    sys.path.append(utils_path)

from WebGLM.model import load_model, citation_correction
from WebGLM.arguments import add_model_config_args
from sentence_transformers import SentenceTransformer
import argparse
from time import time
from pymilvus import MilvusClient
from tool_base import toolbase


class LibWebSearch(toolbase):
    def __init__(self, agent=None):
        super().__init__(agent)
        self.description = "获取回答问题所需的知识"
        self.intention = "获取能够回答问题的外部参考信息" #参考信息
        self.toolcode = "lib_web_search"
        #知识库检索和外部检索应该不需要参数补全，只需要一个query即可
        self.top_k = 10
        self.embedding_model = SentenceTransformer('/home/langchao/IOAAgentApi/utils/WebGLM/MokaAI/m3e-base')
        self.COLLECTION_NAME = "WuYeKnowledgeLib"
        self.client = MilvusClient(
            "http://localhost:19530"
        )
        # self.uri = "http://localhost:19530"


    # def run(self, history, query):
    #     result = self.agent.input(history).instruct(f'找出能够回答这个问题的参考信息:{query}').start()
    def run(self, history=None):
        workflow = Agently.Workflow()
        top_k = self.top_k
        embedding_model = self.embedding_model
        COLLECTION_NAME = self.COLLECTION_NAME
        client = self.client 
        tool_agent = agent_factory.create_agent()
        print("history:",history)
        query = history[-1]['user_input']

        @workflow.chunk()
        def retrieve_from_lib(self, storage):    #向量检索
            # top_k = self.top_k
            # client = MilvusClient(
            #     self.uri
            # )
            # print("[query]:  ", [query])  #[query]:   [[{'user_input': '星舰四飞结果如何', 'model_output': '获取能够回答问题的外部参考信息'}]]
            # print(query[0]['user_input'])
            
            
            query_vectors = embedding_model.encode([query])
            try:
                res = client.search(
                    collection_name=COLLECTION_NAME,     # target collection
                    data=query_vectors,                # query vectors
                    limit=top_k,                           # number of returned entities
                    output_fields=["content", "content_id", "file_name", "file_id", "project_id"]
                )
            except Exception as e:
                print("Error: " + str(e))
                return str(e), 500

            res1 = [item['entity']['content'] for sublist in res for item in sublist]
            retrieve_result = '\n'.join(res1)
            storage.set("ref", retrieve_result)

            return retrieve_result
        
        @workflow.chunk()
        def decide_if_websearch(self, storage):  #判断检索出来的内容是否已经足够作为参考信息
            lib_ref = storage.get("ref")
            nonlocal history
            print("lib_ref:", lib_ref)
            
            prompt = f'现在有一个问题:{query}\n以及它的参考信息:\n{lib_ref}\n请判断\
            # 参考信息是否足够回答问题，如果足够，请回答1；否则回答0。'
           
            start_time = time()
            outputs = tool_agent.input(history).instruct(prompt).start()
            print({"answer": outputs})
            # print("产生答案用时： %s seconds" % (time() - start_time))
            if_search = outputs

            return if_search
            
        @workflow.chunk()
        def retrieve_from_web(self, storage):
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
            storage.set("ref", references)
            return references

        @workflow.chunk()
        def conclude(self, storage):
            # return inputs["default"]
            # return storage.get("ref")
            prompt = f'现在有一个问题:{query}\n以及它的参考信息:\n{storage.get("ref")}\n请根据参考信息回答该问题。'
            output = tool_agent.input(history).instruct(prompt).start()
            return output

        (
            workflow
                .connect_to("retrieve_from_lib")
                .connect_to("decide_if_websearch")
                .if_condition(lambda return_value, storage: int(return_value) > 0)
                    .connect_to("conclude")
                .else_condition()
                    .connect_to("retrieve_from_web")
                    .connect_to("conclude")
        )

        workflow.chunks["conclude"].connect_to("END")
        result = workflow.start()
        # result = workflow.start(
        #     "",
        #     storage={ "ref": "" }
        # )
        print("tool输出为：", result)
