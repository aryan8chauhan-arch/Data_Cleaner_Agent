import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

from env import DataCleaningEnv
from models import Action

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
API_KEY = os.getenv("HF_TOKEN")

BENCHMARK = "data-cleaner-pro"
MAX_STEPS = 10
MAX_TOTAL_REWARD = 1.0 
SUCCESS_SCORE_THRESHOLD = 0.5

SYSTEM_PROMPT = """
You are an expert Python data scientist. Your task is to clean a dataset.
You will receive a summary of the current dataset.
You MUST reply with exactly ONE action using this strict JSON format:

{"command": "drop_duplicates", "column": null, "value": null}
or
{"command": "fill_na", "column": "Age", "value": 0}
or
{"command": "drop_column", "column": "Salary", "value": null}
or
{"command": "clean_currency", "column": "Revenue", "value": null}

CRITICAL: If you use 'fill_na', you MUST provide a real number or string in the 'value' field. Do not use null for the value.
Only output valid JSON. Do not include markdown formatting, backticks, or explanations.
"""

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str = None) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def parse_action(response_text: str) -> Action:
    try:
        clean_text = re.sub(r"```json|```", "", response_text).strip()
        action_dict = json.loads(clean_text)
        return Action(**action_dict), None
    except Exception as e:
        return Action(command="noop"), str(e)

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = DataCleaningEnv()
    
    tasks = [
        "remove_duplicates", 
        "drop_empty_columns", 
        "handle_missing_values", 
        "standardize_currency", 
        "format_consistency", 
        "gdpr_pii_redaction"
    ]

    for task_id in tasks:
        log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
        
        obs = env.reset(task_id=task_id)
        
        rewards = []
        steps_taken = 0
        success = False
        
        for step in range(1, env.max_steps + 1):
            user_prompt = f"Data Preview:\n{obs.data_preview}\nNull Counts: {obs.null_counts}\nFeedback: {obs.message}"
            
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                )
                ai_text = response.choices[0].message.content
                action, parse_error = parse_action(ai_text)
            except Exception as e:
                action = Action(command="noop")
                parse_error = f"API Error: {str(e)}"
            
            action_str = f"{action.command}({action.column})"
            
            obs, raw_reward, done, info = env.step(action)
            
            reward = min(max(raw_reward, 0.0), 1.0)
            
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action_str, reward=reward, done=done, error=parse_error)
            
            if done:
                break
        '''
        if done and raw_reward >= 1.0:
            score = 1.0
        else:
            score = sum(rewards) / float(env.max_steps)
            score = min(max(score, 0.0), 1.0)
        '''

        if done and raw_reward >= 1.0:
            score = 0.999
        else:
            score = sum(rewards) / float(env.max_steps)
            score = min(max(score, 0.001), 0.999)

        success = score >= SUCCESS_SCORE_THRESHOLD
        
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    main()
