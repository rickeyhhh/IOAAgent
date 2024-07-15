import Agently
import os
import sys

# # 检查当前工作目录
# print("Current working directory:", os.getcwd())
print(sys.path)
# 如果utils不在当前目录或子目录中，添加其路径
utils_path = '/home/langchao/IOAAgentApi/utils'  # 替换为utils包的实际路径
if utils_path not in sys.path:
    sys.path.append(utils_path)
print(sys.path)
from WebGLM.model import load_model, citation_correction
from WebGLM.arguments import add_model_config_args
from sentence_transformers import SentenceTransformer
import argparse
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility, MilvusClient
import time

from transformers import AutoTokenizer, AutoModel

from tool_base import toolbase

top_k = 10
embedding_model = SentenceTransformer('/home/langchao/IOAAgentApi/utils/WebGLM/MokaAI/m3e-base')
COLLECTION_NAME = "WuYeKnowledgeLib"
query="星舰四飞结果如何"
# query="保安主管的职权有哪些？"


tokenizer = AutoTokenizer.from_pretrained('/home/langchao/IOAAgentApi/utils/WebGLM/ZhipuAI/chatglm3-6b', trust_remote_code=True)
model = AutoModel.from_pretrained('/home/langchao/IOAAgentApi/utils/WebGLM/ZhipuAI/chatglm3-6b', trust_remote_code=True, device='cuda')
model.to('cuda')
model.eval()     

workflow = Agently.Workflow()
@workflow.chunk()
def retrieve_from_lib(inputs, storage):    #向量检索
    client = MilvusClient(
        uri="http://localhost:19530"
    )
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
    # print("知识库搜索：",retrieve_result)
    return retrieve_result

@workflow.chunk()
def decide_if_websearch(inputs, storage):  #判断检索出来的内容是否已经足够作为参考信息
    lib_ref = inputs["default"]
    storage.set("ref", lib_ref)

    print("lib_ref:",lib_ref)
   
    prompt = f'现在有一个问题:{query}\n以及它的参考信息:\n{lib_ref}\n请判断\
    # 参考信息是否足够回答问题，如果足够，请回答1；否则回答0。'

    print("prompt: ",prompt)
    
    start_time = time.time()
    outputs, history = model.chat(tokenizer, prompt, history=[])
    print({"answer": outputs})
    print("产生答案用时： %s seconds" % (time.time() - start_time))
    if_search = outputs

    return if_search
    
@workflow.chunk()
def retrieve_from_web(inputs, storage):
    arg = argparse.ArgumentParser()
    add_model_config_args(arg)
    args = arg.parse_args()
    webglm = load_model(embedding_model, args)
    question = query
    start_time = time.time()  #测试时间
    question = question.strip()
    final_results = {}
    output = webglm.stream_query(question)

    print("Time taken: %.2f seconds"%(time.time() - start_time))
    references = [ref['text'] for ref in output]
    references = '\n'.join(references)
    storage.set("ref", references)
    return references

@workflow.chunk()
def conclude(inputs, storage):
    # return inputs["default"]
    return storage.get("ref")

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
# result = result = workflow.start(
#     "Hello Agently", 
#     storage={ "init_storage": "Hello Agently Workflow" }
# )
result = result = workflow.start(
    storage={ "ref": "" }
)
print(result)

#问题参考信息采用知识库还是网页检索的内容？

if __name__ == "__main__":
    query="保安主管的职责"
    client = MilvusClient(
        uri="http://localhost:19530"
    )
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
        
    res1 = [item['entity']['content'] for sublist in res for item in sublist]
    retrieve_result = '\n'.join(res1)
    # print("知识库搜索：",retrieve_result)
    print(retrieve_result)