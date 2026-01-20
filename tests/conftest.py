import pytest

def pytest_addoption(parser):
    # コマンドラインから各種引数を受け取る
    parser.addoption("--id-token", action="store", default="", help="API認証用のid token")
    parser.addoption("--upn", action="store", default="llm_azure@estyle-inc.jp", help="ユーザープリンシパルネーム")
    parser.addoption("--mail", action="store", default="llm_azure@estyle-inc.jp", help="API認証用のメールアドレス")


@pytest.fixture
def id_token(request):
    return request.config.getoption("--id-token")

@pytest.fixture
def upn(request):
    return request.config.getoption("--upn")

@pytest.fixture
def mail(request):
    return request.config.getoption("--mail")