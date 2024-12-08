from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class StateChange(BaseModel):
    change: Literal['set', 'append', 'remove']
    field: str
    value: str

class StateChanges(BaseModel):
    changes: List[StateChange] = None

    def add_change(self, change: StateChange):
        if self.changes is None:
            self.changes = []
        self.changes.append(change)


class Job(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    wishes: List[str] = Field(default_factory=list)


class PreviousRole(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    years: Optional[int] = None
    description: Optional[str] = None


class Experience(BaseModel):
    years: Optional[int] = None
    previous_employers: List[str] = Field(default_factory=list)
    current: Optional[str] = None
    previous_roles: List[PreviousRole] = Field(default_factory=list)


class LLMState(BaseModel):
    vacancy: Job = Job()
    experience: Experience = Experience()
