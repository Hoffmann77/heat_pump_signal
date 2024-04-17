"""Utils module."""

from typing import Any

from homeassistant.core import State
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

ERROR_STATES = {STATE_UNAVAILABLE, STATE_UNKNOWN}



def get_state(states: dict, entity_id: str, default: Any = None):
    """Return the state of the given entity."""
    



def get_state_as_float(
        states: dict,
        entity_id: str,
        default: Any = None,
        normalize: bool = True,
) -> float:
    """Return the state of the given entity as float.
            

    Parameters
    ----------
    states : dict
        Homeassistant instance states dict.
    entity_id : str
        Entity id of the state.
    default : float, optional
        Dafault return value. The default is 0.
    normalize : bool, optional
        Whether to normalize the value. The default is True.

    Returns
    -------
    float
        DESCRIPTION.

    """
    
    state_obj = states.get(entity_id)

    if state_obj is None:
        return None
    elif state_obj.state in {STATE_UNAVAILABLE, STATE_UNKNOWN}:
        return state_obj.state
    
    try:
        value = float(state_obj.state)
    except ValueError:
        return state_obj.state
        
    if normalize:
        unit = state_obj.attributes.get("unit_of_measurement")
        if len(unit) > 2:
            if unit[0] == "k":
                return value * 10**3
            elif unit[0] == "M":
                return value * 10**6            
    
    return value
    

    
    



class StateDescriptor:
    """Descriptor class handling access to hass states."""
    
    def __init__(
            self,
            default=None,
            convert_to=None,
            normalize_unit=True
    ) -> None:
        """Initialize instance.

        Parameters
        ----------
        default : TYPE, optional
            Default value that is returned if `self.entity_id` is None.
            The default is None.
        convert_to : TYPE, optional
            . The default is None.
        normalize_unit : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None
            DESCRIPTION.

        """
        
        
        
        self.default = default
        self.convert_to = convert_to
        self.normalize_unit = normalize_unit

    def __set_name__(self, owner, name) -> None:
        """Set the owner and name of the descriptor."""
        self.private_name = "_" + name

    def __get__(self, obj, objtype=None):
        """Dunder method."""
        # entity_id = getattr(obj, self.private_name)
        entity_id = self.entitiy_id

        if entity_id is None:
            return self.default

        state_obj = obj.hass.states.get(entity_id)
        if state_obj is None: # or state_obj.state in ERROR_STATES:
            return None
        elif state_obj.state in ERROR_STATES:
            return state_obj.state
        elif self.convert_to is not None:
            return self.convert(state_obj)
        else:
            return state_obj.state

    def __set__(self, obj, value):
        """Dunder method."""
        setattr(obj, self.private_name, value)
        self.entitiy_id = value

    def convert(self, state_obj):
        """Convert the state."""
        if self.convert_to is float:
            unit = state_obj.attributes.get("unit_of_measurement")
            state = self.convert_to(state_obj.state)
            if len(unit) < 2 or not self.normalize_unit:
                return state
            match unit[0]:
                case "k":
                    return state * 10**3
                case "M":
                    return state * 10**6

            return float(state_obj.state)
        else:
            return self.convert_to(state_obj.state)

