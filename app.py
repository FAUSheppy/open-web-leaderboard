import server
def createApp(envivorment=None, start_response=None):
    with server.app.app_context():
        server.create_app()
    return server.app
