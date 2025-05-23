from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote
from uuid import uuid4

from lime_python import Command, CommandMethod, Message, Node, Identity, Document
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

DEFAULT_BROADCAST_DOMAIN = "broadcast.msging.net"


class DocumentCollection:
    """Represents a collection of documents."""
    
    def __init__(self, items: List[Any] = None, total: int = 0):
        self.items = items or []
        self.total = total


class BroadcastExtension(ExtensionBase):
    """
    Provide a distribution list management service for message broadcasting.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._distribution_list_address = Node("postmaster", DEFAULT_BROADCAST_DOMAIN, None)

    async def create_distribution_list_async(self, list_name: str) -> None:
        """
        Creates a distribution list with the specified name.
        
        Args:
            list_name: Name of the list
        """
        if not list_name or list_name.isspace():
            raise ValueError("The list name cannot be null or whitespace.")
            
        list_identity = self.get_list_identity(list_name)
        
        resource = {
            "identity": str(list_identity)
        }
        
        command = self.create_set_command("/lists", resource, "application/vnd.iris.distribution-list+json")
        command.to = self._distribution_list_address
        
        await self.process_command_async(command)

    async def get_all_distribution_lists_async(self, skip: int = 0, take: int = 100) -> DocumentCollection:
        """
        Gets all existing distribution lists.
        
        Args:
            skip: The number to skip
            take: The number to take
            
        Returns:
            DocumentCollection: Collection of distribution lists
        """
        command = self.create_get_command("/lists")
        command.to = self._distribution_list_address
        
        result = await self.process_command_async(command)
        return self._parse_document_collection(result)

    async def delete_distribution_list_async(self, list_name: str) -> None:
        """
        Deletes an existing distribution list.
        
        Args:
            list_name: Name of the list
        """
        list_identity = self.get_list_identity(list_name)
        uri = f"/lists/{quote(str(list_identity), safe='')}"
        
        command = self.create_delete_command(uri)
        command.to = self._distribution_list_address
        
        await self.process_command_async(command)

    async def add_recipient_async(self, list_name: str, recipient_identity: Identity) -> None:
        """
        Adds a recipient identity to an existing distribution list.
        
        Args:
            list_name: Name of the list
            recipient_identity: The recipient identity
        """
        if not recipient_identity:
            raise ValueError("recipientIdentity cannot be null")
            
        list_identity = self.get_list_identity(list_name)
        uri = f"/lists/{quote(str(list_identity), safe='')}/recipients"
        
        resource = {
            "value": str(recipient_identity)
        }
        
        command = self.create_set_command(uri, resource, "application/vnd.lime.identity+json")
        command.to = self._distribution_list_address
        
        await self.process_command_async(command)

    async def delete_recipient_async(self, list_name: str, recipient_identity: Identity) -> None:
        """
        Deletes a recipient identity from an existing distribution list.
        
        Args:
            list_name: Name of the list
            recipient_identity: The recipient identity
        """
        if not recipient_identity:
            raise ValueError("recipientIdentity cannot be null")
            
        list_identity = self.get_list_identity(list_name)
        uri = f"/lists/{quote(str(list_identity), safe='')}/recipients/{quote(str(recipient_identity), safe='')}"
        
        command = self.create_delete_command(uri)
        command.to = self._distribution_list_address
        
        await self.process_command_async(command)

    async def has_recipient_async(self, list_name: str, recipient_identity: Identity) -> bool:
        """
        Determines whether the distribution list has the specified recipient.
        
        Args:
            list_name: Name of the list
            recipient_identity: The recipient identity
            
        Returns:
            bool: True if recipient exists in list
        """
        if not recipient_identity:
            raise ValueError("recipientIdentity cannot be null")
            
        list_identity = self.get_list_identity(list_name)
        uri = f"/lists/{quote(str(list_identity), safe='')}/recipients/{quote(str(recipient_identity), safe='')}"
        
        command = self.create_get_command(uri)
        command.to = self._distribution_list_address
        
        try:
            await self.process_command_async(command)
            return True
        except Exception:
            # In case of resource not found or any error, return False
            return False

    async def get_recipients_async(self, list_name: str, skip: int = 0, take: int = 100) -> DocumentCollection:
        """
        Gets the recipients of the specified list.
        
        Args:
            list_name: Name of the list
            skip: The number to skip
            take: The number to take
            
        Returns:
            DocumentCollection: Collection of recipients
        """
        list_identity = self.get_list_identity(list_name)
        uri = f"/lists/{quote(str(list_identity), safe='')}/recipients?$skip={skip}&$take={take}"
        
        command = self.create_get_command(uri)
        command.to = self._distribution_list_address
        
        result = await self.process_command_async(command)
        return self._parse_document_collection(result)

    def get_list_identity(self, list_name: str) -> Identity:
        """
        Gets the list identity from a name.
        
        Args:
            list_name: Name of the list
            
        Returns:
            Identity: The list identity
        """
        if not list_name or list_name.isspace():
            raise ValueError("The list name cannot be null or whitespace.")
            
        return Identity(list_name, self._distribution_list_address.domain)

    async def send_message_async(self, list_name: str, content: Document, id: str = None) -> None:
        """
        Sends a message to a distribution list with the specified content.
        
        Args:
            list_name: Name of the list
            content: The content
            id: Optional message ID
        """
        message = Message(
            id=id or str(uuid4()),
            to=self.get_list_identity(list_name).to_node(),
            content=content
        )
        
        await self.client.send_message_async(message)

    def _parse_document_collection(self, result: Command) -> DocumentCollection:
        """Parse document collection from command response."""
        if result.resource and isinstance(result.resource, dict):
            items = result.resource.get('items', [])
            total = result.resource.get('total', len(items))
            return DocumentCollection(items, total)
        return DocumentCollection()