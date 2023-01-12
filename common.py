from dataclasses import dataclass

@dataclass(eq=True)
class Event():
  name: str # name of the event
  source: str # name of the process that generated the event
  destination: str # name of the process that will receive the event
  data: dict # data associated with the event