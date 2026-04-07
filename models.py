from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Action(BaseModel):
    
    command: str = Field(
        description="The action to take: 'drop_duplicates', 'fill_na', 'drop_column', or 'clean_currency' (removes $ and commas)"
    )
    column: Optional[str] = Field(
        default=None, 
        description="The name of the column to act upon (required for fill_na and drop_column)"
    )
    value: Optional[Any] = Field(
        default=None, 
        description="The value to use when filling missing data (e.g., 0 or 'Unknown')"
    )

class Observation(BaseModel):
    
    data_preview: str = Field(description="A text-based snippet of the first few rows (df.head())")
    column_info: Dict[str, str] = Field(description="Mapping of column names to their data types")
    null_counts: Dict[str, int] = Field(description="Number of missing values per column")
    message: str = Field(description="Feedback from the last action taken")

class Reward(BaseModel):
    
    value: float = Field(description="The score for the current step (0.0 to 1.0)")
    is_terminal: bool = Field(description="Whether the cleaning task is finished")
