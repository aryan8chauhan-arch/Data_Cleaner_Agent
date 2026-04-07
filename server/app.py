from openenv.core.env_server import create_app
from models import Action, Observation
from env import DataCleaningEnv
import uvicorn

app = create_app(DataCleaningEnv, Action, Observation, env_name="data-cleaner-pro")

# OpenEnv looks for this exact function to start the server locally
def run():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)