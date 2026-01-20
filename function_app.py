import azure.functions as func
import azure.durable_functions as d_func
import logging

# サンプルのコードをインポート
from blueprints.activity import activity_sample_bp
from blueprints.orchestrator import orchestrator_sample_bp

# エージェント用のコードをインポート
from blueprints.activity import activity_init_agent_bp, activity_choose_tool_bp, activity_call_tool_bp, activity_add_history_bp, activity_process_messages_bp, activity_check_mode_permission_bp
from blueprints.orchestrator import orchestrator_agent_bp


# 初期化
app = d_func.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

# サンプル用のblueprintを登録
app.register_blueprint(activity_sample_bp)
app.register_blueprint(orchestrator_sample_bp)

# エージェント用のblueprintを登録
app.register_blueprint(activity_init_agent_bp)
app.register_blueprint(activity_choose_tool_bp)
app.register_blueprint(activity_call_tool_bp)
app.register_blueprint(activity_add_history_bp)
app.register_blueprint(activity_process_messages_bp)
app.register_blueprint(activity_check_mode_permission_bp)
app.register_blueprint(orchestrator_agent_bp)


@app.route(route="durable/{functionName}")
@app.durable_client_input(client_name="client")
async def start_orchestrator(req: func.HttpRequest, client):
    """
    durable functionsの呼び出し用のAPI
    postされたデータを読み込み、urlにて指定された関数を呼び出す
    """
    payload: dict = req.get_json()
    instance_id = await client.start_new(req.route_params["functionName"], client_input=payload)

    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    return client.create_check_status_response(req, instance_id)

