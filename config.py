import os
from azure.storage.blob.aio import BlobServiceClient
from i_style.llm import ModelRegistry, ModelConfig
from i_style.text_extractor import FileTextExtractor

# 共通設定
MCP_CODE = os.environ.get("MCP_CODE", "")
MCP_HOST_NAME = os.environ.get("MCP_HOST_NAME", "localhost:3000")
if MCP_HOST_NAME.startswith("localhost"):
    MCP_SERVER_FUNC_NAME = f"http://{MCP_HOST_NAME}"
else:
    MCP_SERVER_FUNC_NAME = f"https://{MCP_HOST_NAME}"

LLM_REGISTRY = ModelRegistry(enable_models=["aoai","gemini"])

# max_tokensの上書き
_registered_models = set(LLM_REGISTRY.list_models())
for model_name in {"o3-mini", "o4-mini", "o1", "o3"}:
    if model_name in _registered_models:
        LLM_REGISTRY.models[model_name].max_tokens["output"] = 20_000

RESEARCH_REGISTRY = ModelRegistry(enable_models=["aoai"])
research_models_data = {
    "gpt4.1": {
        "endpoint": os.environ.get("RESEARCH_GPT4_1_API_ENDPOINT"),
        "key": os.environ.get("RESEARCH_GPT4_1_API_KEY"),
        "deployment_name": os.environ.get("RESEARCH_GPT4_1_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 1_047_576, "output": 32_768},
        "service": "aoai",
    },
    "o3": {
        "endpoint": os.environ.get("RESEARCH_O3_API_ENDPOINT"),
        "key": os.environ.get("RESEARCH_O3_API_KEY"),
        "deployment_name": os.environ.get("RESEARCH_O3_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 200_000, "output": 20_000}, # 出力トークンを上書き
        "service": "aoai",
    },
    "o4-mini": {
        "endpoint": os.environ.get("RESEARCH_O4_MINI_API_ENDPOINT"),
        "key": os.environ.get("RESEARCH_O4_MINI_API_KEY"),
        "deployment_name": os.environ.get("RESEARCH_O4_MINI_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 200_000, "output": 20_000}, # 出力トークンを上書き
        "service": "aoai",
    },
    "gpt5": {
        "endpoint": os.environ.get("RESEARCH_GPT5_API_ENDPOINT"),
        "key": os.environ.get("RESEARCH_GPT5_API_KEY"),
        "deployment_name": os.environ.get("RESEARCH_GPT5_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 272_000, "output": 128_000},
        "service": "aoai",
    },
}

for model_name, config in research_models_data.items():
    if config["endpoint"] and config["deployment_name"]:
        if config.get("key"):
            RESEARCH_REGISTRY.models[model_name] = ModelConfig(**config)

COMPANY_REGISTRY = ModelRegistry(enable_models=["aoai"])
company_models_data = {
    "gpt4.1": {
        "endpoint": os.environ.get("COMPANY_GPT4_1_API_ENDPOINT"),
        "key": os.environ.get("COMPANY_GPT4_1_API_KEY"),
        "deployment_name": os.environ.get("COMPANY_GPT4_1_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 1_047_576, "output": 32_768},
        "service": "aoai",
    },
    "o3": {
        "endpoint": os.environ.get("COMPANY_O3_API_ENDPOINT"),
        "key": os.environ.get("COMPANY_O3_API_KEY"),
        "deployment_name": os.environ.get("COMPANY_O3_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 200_000, "output": 20_000}, # 出力トークン数を上書き
        "service": "aoai",
    },
    "o4-mini": {
        "endpoint": os.environ.get("COMPANY_O4_MINI_API_ENDPOINT"),
        "key": os.environ.get("COMPANY_O4_MINI_API_KEY"),
        "deployment_name": os.environ.get("COMPANY_O4_MINI_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 200_000, "output": 20_000}, # 出力トークン数を上書き
        "service": "aoai",
    },
    "gpt5": {
        "endpoint": os.environ.get("COMPANY_GPT5_API_ENDPOINT"),
        "key": os.environ.get("COMPANY_GPT5_API_KEY"),
        "deployment_name": os.environ.get("COMPANY_GPT5_DEPLOYMENT_NAME"),
        "max_tokens": {"input": 272_000, "output": 128_000},
        "service": "aoai",
    },
}

for model_name, config in company_models_data.items():
    if config["endpoint"] and config["deployment_name"]:
        if config.get("key"):
            COMPANY_REGISTRY.models[model_name] = ModelConfig(**config)

HISTORY_API_URL = os.environ.get("HISTORY_API_URL", "http://localhost:7071")
HISTORY_API_KEY = os.environ.get("HISTORY_API_KEY")

# ファイル添付、出力用のblob
BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(os.environ.get("BLOB_CONNECTION_STRING"))
FILE_CONTAINER_NAME = "file-data"

# 添付ファイルの文字起こしに対応する拡張子を設定
FILE_EXTENSIONS = ["pdf", "pptx", "docx", "csv", "msg", "xlsx", "txt", "jpg", "jpeg", "png", "tiff", "eml"]
FILE_TEXT_EXTRACTOR = FileTextExtractor(
    file_extension_list=FILE_EXTENSIONS,
    model_registry=ModelRegistry(),
    # その他はデフォルトのパラメータを使用
)

# 権限制御用(check_permission)
GENIE_AUTH_URL = os.environ.get("GENIE_AUTH_URL")
GENIE_AUTH_API_KEY = os.environ.get("GENIE_AUTH_API_KEY")