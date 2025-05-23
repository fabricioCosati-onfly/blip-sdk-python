from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional
from datetime import datetime

from lime_python import Command, Node, Message
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

DEFAULT_SCHEDULER_DOMAIN = "scheduler.msging.net"
POSTMASTER = "postmaster"


class ScheduledMessage:
    """Represents a scheduled message."""
    
    def __init__(self, when: datetime, message: Message, name: str = None):
        self.when = when
        self.message = message
        self.name = name


class SchedulerExtension(ExtensionBase):
    """
    Provides message scheduling functionality.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._scheduler_address = Node(POSTMASTER, DEFAULT_SCHEDULER_DOMAIN, None)

    async def schedule_message_async(self, when: datetime, message: Message, name: str = None) -> None:
        """
        Schedule a message to be sent at a specific time.
        
        Args:
            when: When to send the message
            message: The message to send
            name: Optional name for the scheduled message
        """
        scheduled_data = {
            "when": when.isoformat(),
            "message": {
                "to": str(message.to),
                "content": message.content,
                "type": getattr(message, 'type', None)
            }
        }
        
        if name:
            scheduled_data["name"] = name

        command = self.create_set_command("/messages", scheduled_data)
        command.to = self._scheduler_address
        
        await self.process_command_async(command)

    async def cancel_scheduled_message_async(self, name: str) -> None:
        """
        Cancel a scheduled message by name.
        
        Args:
            name: The name of the scheduled message to cancel
        """
        if not name:
            raise ValueError("name cannot be null or empty")

        command = self.create_delete_command(f"/messages/{name}")
        command.to = self._scheduler_address
        
        await self.process_command_async(command)

    async def get_scheduled_messages_async(self, skip: int = 0, take: int = 100) -> list:
        """
        Get list of scheduled messages.
        
        Args:
            skip: Number of items to skip
            take: Number of items to take
            
        Returns:
            list: List of scheduled messages
        """
        uri = f"/messages?$skip={skip}&$take={take}"
        command = self.create_get_command(uri)
        command.to = self._scheduler_address
        
        result = await self.process_command_async(command)
        return self._parse_scheduled_messages_response(result)

    def _parse_scheduled_messages_response(self, result: Command) -> list:
        """Parse scheduled messages from command response."""
        if result.resource and isinstance(result.resource, dict):
            items = result.resource.get('items', [])
            return items
        return []