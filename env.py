import pandas as pd
from models import Action, Observation
from openenv.core.env_server import Environment

class DataCleaningEnv(Environment):
    def __init__(self):
        super().__init__()
        self.df = None
        self.step_count = 0
        self.max_steps = 10
        self.current_task = None
    def reset(self, task_id: str = "remove_duplicates", **kwargs) -> Observation:
    #def reset(self, task_id: str = "remove_duplicates") -> Observation:
        """API to restart the environment and load the specific task data."""
        self.current_task = task_id
        self.step_count = 0

        if task_id == "remove_duplicates":
            data = {'ID': [1, 2, 2, 3], 'Name': ['Alice', 'Bob', 'Bob', 'Charlie']}

        elif task_id == "drop_empty_columns":
            data = {
                'User_ID': [101, 102, 103],
                'Name': ['Alice', 'Bob', 'Charlie'],
                'Unnamed: 2': [None, None, None] 
            }
        
        elif task_id == "handle_missing_values":
            data = {'ID': [1, 2, 3], 'Age': [25, None, 30], 'Salary': [50000, 60000, None]}

        elif task_id == "standardize_currency":
            data = {'ID': [1, 2, 3], 'Revenue': ['$1,000.50', '$2,500.00', '$3,000.75']}

        elif task_id == "gdpr_pii_redaction":
            data = {
                'Transaction_ID': [101, 102, 103],
                'User_Meta_1': ['user123@gmail.com', 'john.doe@yahoo.com', 'admin@company.com'],
                'User_Meta_2': ['Active', 'Suspended', 'Active']
            }
        
        else: 
            data = {'ID': [1, 2, 3], 'Price': ['10', None, '20.5'], 'Status': ['Active', 'active', 'Inactive']}

        self.df = pd.DataFrame(data)
        return self._get_obs(f"Environment reset for task: {task_id}. Ready to clean.")

    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        """The main loop: The agent takes an Action, we return the new state and a Reward."""
        self.step_count += 1
        reward = 0.0
        msg = ""

        try:
            if action.command == "drop_duplicates":
                initial_rows = len(self.df)
                self.df = self.df.drop_duplicates()
                if len(self.df) < initial_rows:
                    reward = 0.5
                    msg = f"Success! Dropped {initial_rows - len(self.df)} duplicate rows."
                else:
                    reward = -0.1
                    msg = "Failed. No duplicates were found to drop."

            elif action.command == "fill_na":
                if action.column in self.df.columns:
                    if action.value is None:
                        reward = -0.2
                        msg = "Failed. You must provide a 'value' to replace the nulls with."
                    else:
                        initial_nulls = self.df[action.column].isnull().sum()
                        self.df[action.column] = self.df[action.column].fillna(action.value)
                        
                        if self.df[action.column].isnull().sum() < initial_nulls:
                            reward = 0.5
                            msg = f"Success! Filled missing values in '{action.column}' with '{action.value}'."
                        else:
                            reward = -0.1
                            msg = f"Failed. No missing values were found to replace in '{action.column}'."
                else:
                    reward = -0.2
                    msg = f"Error: Column '{action.column}' does not exist."

            elif action.command == "drop_column":
                if action.column in self.df.columns:
                    self.df = self.df.drop(columns=[action.column])
                    reward = 0.2
                    msg = f"Success! Dropped column '{action.column}'."
                else:
                    reward = -0.2
                    msg = f"Error: Column '{action.column}' does not exist."

            elif action.command == "clean_currency":
                if action.column in self.df.columns:
                    try:
                        self.df[action.column] = self.df[action.column].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
                        reward = 0.5
                        msg = f"Success! Cleaned currency formatting in '{action.column}'."
                    except Exception as e:
                        reward = -0.2
                        msg = f"Failed to clean currency. Make sure it's a string column. Error: {e}"
                else:
                    reward = -0.2
                    msg = f"Error: Column '{action.column}' does not exist."

            else:
                reward = -0.2
                msg = f"Error: Unknown command '{action.command}'."

        except Exception as e:
            reward = -0.5
            msg = f"Execution Error: {str(e)}"

        is_done = False
        
        if self.current_task == "remove_duplicates" and not self.df.duplicated().any():
            is_done = True
            reward += 1.0
            msg += " Task Complete: All duplicates removed!"
            
        elif self.current_task == "drop_empty_columns":
            if 'Unnamed: 2' not in self.df.columns:
                is_done = True
                reward += 1.0
                msg += " Task Complete: Empty ghost column removed!"

        elif self.current_task == "handle_missing_values" and not self.df.isnull().any().any():
            is_done = True
            reward += 1.0
            msg += " Task Complete: All missing values handled!"

        elif self.current_task == "standardize_currency":
            if pd.api.types.is_float_dtype(self.df['Revenue']):
                is_done = True
                reward += 1.0
                msg += " Task Complete: Currency standardized to floats!"

        elif self.current_task == "format_consistency":
            no_nulls = not self.df.isnull().any().any()
            is_done = no_nulls
            if is_done:
                reward += 1.0
                msg += " Task Complete: Format consistency achieved!"

        elif self.current_task == "gdpr_pii_redaction":
            if 'User_Meta_1' not in self.df.columns and 'User_Meta_2' in self.df.columns:
                is_done = True
                reward += 1.0
                msg += " Task Complete: PII successfully redacted!"

        if self.step_count >= self.max_steps:
            is_done = True
            msg += " Reached maximum steps."

        return self._get_obs(msg), reward, is_done, {}

    def state(self) -> dict:
        return self.df.to_dict()

    def _get_obs(self, msg: str) -> Observation:
        return Observation(
            data_preview=self.df.head().to_string(),
            column_info={col: str(dtype) for col, dtype in self.df.dtypes.items()},
            null_counts={str(k): int(v) for k, v in self.df.isnull().sum().items()},
            #null_counts=self.df.isnull().sum().to_dict(),
            message=msg
        )
