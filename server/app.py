from openenv.core.env_server import create_app
from models import Action, Observation
from env import DataCleaningEnv
import uvicorn

app = create_app(DataCleaningEnv, Action, Observation, env_name="data-cleaner-pro")

# OpenEnv looks for this exact function to start the server locally
# OpenEnv requires this to be named 'main' and have the execution block below
def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()