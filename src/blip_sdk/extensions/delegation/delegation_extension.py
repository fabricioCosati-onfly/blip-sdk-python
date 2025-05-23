from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional

from lime_python import Command, Node, Identity, Message
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

DEFAULT_DELEGATION_DOMAIN = "delegation.msging.net"
POSTMASTER = "postmaster"


class DelegationExtension(ExtensionBase):
    """
    Provides message delegation functionality.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._delegation_address = Node(POSTMASTER, DEFAULT_DELEGATION_DOMAIN, None)

    async def delegate_message_async(self, message: Message, target_identity: Identity) -> None:
        """
        Delegate a message to another identity.
        
        Args:
            message: The message to delegate
            target_identity: The target identity to delegate to
        """
        if not message:
            raise ValueError("message cannot be null")
        if not target_identity:
            raise ValueError("targetIdentity cannot be null")

        delegation_data = {
            "message": {
                "from": str(message.from_n) if message.from_n else None,
                "to": str(message.to),
                "content": message.content,
                "type": getattr(message, 'type', None)
            },
            "targetIdentity": str(target_identity)
        }

        command = self.create_set_command("/delegations", delegation_data)
        command.to = self._delegation_address
        
        await self.process_command_async(command)

    async def get_delegations_async(self, skip: int = 0, take: int = 100) -> list:
        """
        Get list of delegations.
        
        Args:
            skip: Number of items to skip
            take: Number of items to take
            
        Returns:
            list: List of delegations
        """
        uri = f"/delegations?$skip={skip}&$take={take}"
        command = self.create_get_command(uri)
        command.to = self._delegation_address
        
        result = await self.process_command_async(command)
        return self._parse_delegations_response(result)

    def _parse_delegations_response(self, result: Command) -> list:
        """Parse delegations from command response."""
        if result.resource and isinstance(result.resource, dict):
            items = result.resource.get('items', [])
            return items
        return []