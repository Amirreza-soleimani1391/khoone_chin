from dataclasses import dataclass

@dataclass
class Project:
    id: int
    name: str
    style: str
    area: str
    canvas_file: str
    created_at: str
    updated_at: str