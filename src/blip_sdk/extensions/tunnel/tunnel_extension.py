from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional

from lime_python import Command, Node, Identity, Message, Notification
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

DEFAULT_TUNNEL_DOMAIN = "tunnel.msging.net"
POSTMASTER = "postmaster"


class TunnelExtension(ExtensionBase):
    """
    Provides tunnel functionality for connecting different domains/channels.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._tunnel_address = Node(POSTMASTER, DEFAULT_TUNNEL_DOMAIN, None)

    async def forward_message_async(self, message: Message, destination_identity: Identity) -> None:
        """
        Forward a message through the tunnel to a destination identity.
        
        Args:
            message: The message to forward
            destination_identity: The destination identity
        """
        if not message:
            raise ValueError("message cannot be null")
        if not destination_identity:
            raise ValueError("destinationIdentity cannot be null")

        tunnel_data = {
            "message": {
                "from": str(message.from_n) if message.from_n else None,
                "to": str(message.to),
                "content": message.content,
                "type": getattr(message, 'type', None),
                "id": message.id
            },
            "destinationIdentity": str(destination_identity)
        }

        command = self.create_set_command("/messages", tunnel_data)
        command.to = self._tunnel_address
        
        await self.process_command_async(command)

    async def forward_notification_async(self, notification: Notification, destination_identity: Identity) -> None:
        """
        Forward a notification through the tunnel to a destination identity.
        
        Args:
            notification: The notification to forward
            destination_identity: The destination identity
        """
        if not notification:
            raise ValueError("notification cannot be null")
        if not destination_identity:
            raise ValueError("destinationIdentity cannot be null")

        tunnel_data = {
            "notification": {
                "from": str(notification.from_n) if notification.from_n else None,
                "to": str(notification.to),
                "event": notification.event,
                "id": notification.id
            },
            "destinationIdentity": str(destination_identity)
        }

        command = self.create_set_command("/notifications", tunnel_data)
        command.to = self._tunnel_address
        
        await self.process_command_async(command)

    async def create_tunnel_async(self, source_identity: Identity, destination_identity: Identity, 
                                 tunnel_name: str = None) -> Dict:
        """
        Create a tunnel between two identities.
        
        Args:
            source_identity: The source identity
            destination_identity: The destination identity
            tunnel_name: Optional tunnel name
            
        Returns:
            Dict: The created tunnel information
        """
        if not source_identity:
            raise ValueError("sourceIdentity cannot be null")
        if not destination_identity:
            raise ValueError("destinationIdentity cannot be null")

        tunnel_data = {
            "sourceIdentity": str(source_identity),
            "destinationIdentity": str(destination_identity)
        }
        
        if tunnel_name:
            tunnel_data["name"] = tunnel_name

        command = self.create_set_command("/tunnels", tunnel_data)
        command.to = self._tunnel_address
        
        result = await self.process_command_async(command)
        return result.resource if result.resource else {}

    async def get_tunnel_async(self, tunnel_id: str) -> Dict:
        """
        Get a tunnel by ID.
        
        Args:
            tunnel_id: The tunnel ID
            
        Returns:
            Dict: The tunnel information
        """
        if not tunnel_id:
            raise ValueError("tunnelId cannot be null or empty")

        command = self.create_get_command(f"/tunnels/{tunnel_id}")
        command.to = self._tunnel_address
        
        result = await self.process_command_async(command)
        return result.resource if result.resource else {}

    async def delete_tunnel_async(self, tunnel_id: str) -> None:
        """
        Delete a tunnel.
        
        Args:
            tunnel_id: The tunnel ID to delete
        """
        if not tunnel_id:
            raise ValueError("tunnelId cannot be null or empty")

        command = self.create_delete_command(f"/tunnels/{tunnel_id}")
        command.to = self._tunnel_address
        
        await self.process_command_async(command)

    async def get_tunnels_async(self, skip: int = 0, take: int = 100) -> list:
        """
        Get list of tunnels.
        
        Args:
            skip: Number of items to skip
            take: Number of items to take
            
        Returns:
            list: List of tunnels
        """
        uri = f"/tunnels?$skip={skip}&$take={take}"
        command = self.create_get_command(uri)
        command.to = self._tunnel_address
        
        result = await self.process_command_async(command)
        return self._parse_tunnels_response(result)

    def _parse_tunnels_response(self, result: Command) -> list:
        """Parse tunnels from command response."""
        if result.resource and isinstance(result.resource, dict):
            items = result.resource.get('items', [])
            return items
        return []