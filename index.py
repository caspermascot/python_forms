def app(environ, start_response):
    response_body = get_response_body()
    status = "200 OK"
    start_response(status, headers=[])
    return iter([response_body])


def get_response_body():
    return b"Hello, World!"
    # from tests.testForms import LoginForm
    # login = LoginForm()
    # login.is_valid()
    # return login.clean_data()