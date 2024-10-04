import json
from typing import Dict, Optional

from pydantic import BaseModel


class SampleModuleParams(BaseModel):
    param_1: str = "value 1"
    param_2: int = "value 2"

    overwrite: Optional[bool] = False

    def to_dict(self) -> Dict:
        return json.loads(self.model_dump_json())
