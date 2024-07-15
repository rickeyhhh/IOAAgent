import Agently
from knowledge_graph import Knowlegde_graph

agent_factory = (
    Agently.AgentFactory()
        .set_settings("current_model", "OAIClient")
        .set_settings("model.OAIClient.auth.api_key", "nothing")  # 如果不需要 API key，可以为空
        .set_settings("model.OAIClient.options", {"model": "kagentlms_baichuan2_13b_mat"})  # 设置您的模型标识
        .set_settings("model.OAIClient.url", "http://localhost:8888/v1")  # 您本地模型的URL
)

agent = agent_factory.create_agent()
agent.set_settings("is_debug", True)
tls=Knowlegde_graph(agent)
tls.run("")
