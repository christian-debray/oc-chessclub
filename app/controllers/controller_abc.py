from abc import ABC, abstractmethod
from app.views.app_status_view import AppStatusView

class AbstractController(ABC):
    """Base class for all controllers

    A controller
      - pilots the application workflow
      - updates the model on user input
      - updates the view with new data pulled from the model
    """
    pass

class BaseController:
    def __init__(self):
      self.status = AppStatusView()
