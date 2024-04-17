"""Common ABC classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class SignalResponse:
    """Dataclass representing a signal response.

    Parameters
    ----------
    state : bool
        State of the signal.
    optional_states : dict
        Optional states.
    metadata : dict
        Metadata.

    """

    primary_state: bool | None
    optional_states: dict
    metadata: dict
    
    def to_dict(self):
        
        return {
            "primary_state": self.primary_state,
            **self.optional_states,
            **self.metadata
        }


class AbstractBaseSignal(ABC):
    """Abstract Base class representing a signal."""

    signal_key: str

    def __init__(self, hass, config) -> None:
        """Initialize instance.

        Parameters
        ----------
        hass : HomeAssistant
            Instance of HomeAssistant.
        config : dict
            Configuration dict.

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.hass = hass
        self.config = config

    @abstractmethod
    def get_signal(self) -> tuple[bool, dict]:
        """
        

        Returns
        -------
        Tuple[bool, dict]
            DESCRIPTION.

        """
        

