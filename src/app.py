import sys
import traceback
from aiohttp import web
from http import HTTPStatus
from datetime import datetime
from botcopilot.bots import TeamsAIBot
from botbuilder.schema import Activity, ActivityTypes
from aiohttp.web import Request, Response, json_response
from botcopilot.configurations.config import DefaultConfig
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.core import TurnContext, MemoryStorage, ConversationState, UserState
from botbuilder.integration.aiohttp import (
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication,
)

CONFIG = DefaultConfig()

# Create adapter with error handler.
ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))


# Define the error handler
async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )

    # If the channel is the Emulator, send a trace activity with the error message
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

# Create memory storage for conversation state.
memory_storage = MemoryStorage()
conversation_state = ConversationState(memory_storage)
user_state = UserState(memory_storage)

# Create the bot
BOT = TeamsAIBot(conversation_state, user_state)


async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(auth_header, activity, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)


# Health check endpoint
def health_check(req: Request) -> Response:
    return Response(status=HTTPStatus.OK)


# Set up the web application
def func_init(argv=None):
    APP = web.Application(middlewares=[aiohttp_error_middleware])
    APP.router.add_post("/api/messages", messages)
    APP.router.add_get("/hc", health_check)
    return APP


if __name__ == "__main__":
    APP = func_init(None)
    try:
        web.run_app(APP, host=CONFIG.HOST, port=CONFIG.PORT)
    except Exception as error:
        raise error
