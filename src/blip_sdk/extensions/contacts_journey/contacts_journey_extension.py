from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime

from lime_python import Command, CommandMethod, Node
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

CONTACTS_JOURNEY_URI = "/contacts-journey"
DEFAULT_ANALYTICS_DOMAIN = "analytics.msging.net"
POSTMASTER = "postmaster"


class ContactsJourneyNode:
    """Represents a contacts journey node."""
    
    def __init__(self, current_state_id: str, current_state_name: str,
                 previous_state_id: str = None, previous_state_name: str = None,
                 contact_identity: str = None, storage_date: datetime = None):
        self.current_state_id = current_state_id
        self.current_state_name = current_state_name
        self.previous_state_id = previous_state_id
        self.previous_state_name = previous_state_name
        self.contact_identity = contact_identity
        self.storage_date = storage_date or datetime.now()


class ContactsJourneyExtension(ExtensionBase):
    """
    Provides contacts journey tracking functionality.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._analytics_address = Node(POSTMASTER, DEFAULT_ANALYTICS_DOMAIN, None)

    async def add_async(self, state_id: str, state_name: str,
                       previous_state_id: str = None, previous_state_name: str = None,
                       contact_identity: str = None, fire_and_forget: bool = False) -> None:
        """
        Add a contacts journey node.
        
        Args:
            state_id: The current state ID
            state_name: The current state name
            previous_state_id: The previous state ID (optional)
            previous_state_name: The previous state name (optional)
            contact_identity: The contact identity (optional)
            fire_and_forget: Whether to use fire and forget mode
        """
        if not state_id or state_id.isspace():
            raise ValueError("stateId cannot be null or empty")
        if not state_name or state_name.isspace():
            raise ValueError("stateName cannot be null or empty")

        journey_node = ContactsJourneyNode(
            current_state_id=state_id,
            current_state_name=state_name,
            previous_state_id=previous_state_id,
            previous_state_name=previous_state_name,
            contact_identity=contact_identity
        )

        journey_data = {
            "currentStateId": journey_node.current_state_id,
            "currentStateName": journey_node.current_state_name,
            "previousStateId": journey_node.previous_state_id,
            "previousStateName": journey_node.previous_state_name,
            "contactIdentity": journey_node.contact_identity,
            "storageDate": journey_node.storage_date.isoformat()
        }

        if fire_and_forget:
            # Use observe method for fire and forget
            command = Command(CommandMethod.OBSERVE, CONTACTS_JOURNEY_URI, 
                            resource=journey_data)
        else:
            # Use set method for normal processing
            command = Command(CommandMethod.SET, CONTACTS_JOURNEY_URI, 
                            resource=journey_data)

        command.to = self._analytics_address

        if fire_and_forget:
            # For fire and forget, we don't wait for response
            await self.client.send_command_async(command)
        else:
            await self.process_command_async(command)