import ast

class TokenMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
        client = scope["client"]
        bearerString = str(scope['headers'][0][1]).split(" ")
        idToken = bearerString[1]
        print(f"[CLIENT]: {client}")