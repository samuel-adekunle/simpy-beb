from dataclasses import dataclass
from uuid import uuid4

@dataclass(eq=True)
class Event():
  id: str # unique id of the event
  name: str # name of the event
  source: str # name of the process that generated the event
  destination: str # name of the process that will receive the event
  data: dict # data associated with the event

def generate_id() -> str:
  # generate a unique id for the event
  return uuid4().hex

class Process(object):
  def __init__(self, env):
    self.id = generate_id()
    self.env = env
    # Start the run process everytime an instance is created.
    self.action = self.env.process(self.run())

  def run(self):
    raise NotImplementedError("Subclass must implement abstract method")

  def handle_event(self, event):
    raise NotImplementedError("Subclass must implement abstract method")