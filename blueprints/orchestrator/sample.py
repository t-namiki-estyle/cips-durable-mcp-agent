import azure.durable_functions as d_func
import logging

bp = d_func.Blueprint()


@bp.orchestration_trigger(context_name="context")
def greed_manager(context: d_func.DurableOrchestrationContext):
    """
    durable functionsの全体の処理を制御します
    かなり制約が多いため、注意が必要
    """
    # インスタンスIDの取得
    instance_id = context.instance_id
    logging.info(f"context id: {instance_id}")

    # 開始時に渡されたデータを取得
    payload = context.get_input()
    name = payload.get("name")
    if name:
        req_json = {"name": name}
    else:
        req_json = {}
    result = yield context.call_activity("say_hello", req_json)
    return result