import azure.durable_functions as d_func

bp = d_func.Blueprint()

@bp.activity_trigger(input_name="payload")
def say_hello(payload: dict) -> dict:
    """
    sample
    input, outputの型はstrやlistでも可能
    組み込みクラス以外のインスタンスをそのまま渡すことはできないはず
    """
    name = payload.get("name")
    if name:
        response = {"message": f"Hello {name}!"}
    else:
        response = {"message": f"Bye~"}
    return response
