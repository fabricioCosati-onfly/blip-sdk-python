from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import quote
from uuid import uuid4

from lime_python import Command, CommandMethod, Message, Node, Identity, Document
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

DEFAULT_DESK_DOMAIN = "desk.msging.net"
ID_PREFIX = "fwd"


class Ticket:
    """Represents a help desk ticket."""
    
    def __init__(self, id: str = None, status: str = None, customer_identity: str = None, 
                 agent_identity: str = None, context: Any = None):
        self.id = id
        self.status = status
        self.customer_identity = customer_identity
        self.agent_identity = agent_identity
        self.context = context


class HelpDeskExtension(ExtensionBase):
    """
    Provide human attendance forwarding, using BLiP HelpDesks module.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._desk_node = Node("postmaster", DEFAULT_DESK_DOMAIN, None)

    async def forward_message_to_agent_async(self, message: Message) -> None:
        """
        Forward a message to active HelpDesk application.
        
        Args:
            message: The message to be forwarded to BLIP HelpDesk agents
        """
        customer_name = quote(str(message.from_n), safe='')
        desk_identity = Identity(customer_name, DEFAULT_DESK_DOMAIN)
        desk_node = desk_identity.to_node()

        fw_message = Message(
            id=f"{ID_PREFIX}:{message.id or str(uuid4())}",
            to=desk_node,
            content=message.content
        )

        await self.client.send_message_async(fw_message)

    def is_from_agent(self, message: Message) -> bool:
        """
        Check if a message is a reply from a BLIP HelpDesks application.
        
        Args:
            message: The Message that must be analyzed
            
        Returns:
            bool: True if message is from agent
        """
        return message.from_n and message.from_n.domain == DEFAULT_DESK_DOMAIN

    async def create_ticket_async(self, customer_identity: Identity, 
                                context: Document = None) -> Ticket:
        """
        Create a ticket with customer identity and context.
        
        Args:
            customer_identity: The customer identity
            context: The document to be sent to agent as an initial context
            
        Returns:
            Ticket: The created ticket
        """
        uri = f"/tickets/{quote(str(customer_identity), safe='')}"
        command = self.create_set_command(uri, context)
        command.to = self._desk_node
        
        result = await self.process_command_async(command)
        return self._parse_ticket_response(result)

    async def create_ticket_with_data_async(self, ticket: Ticket) -> Ticket:
        """
        Create a ticket with ticket data.
        
        Args:
            ticket: The ticket object to create
            
        Returns:
            Ticket: The created ticket
        """
        command = self.create_set_command("/tickets", ticket.__dict__)
        command.to = self._desk_node
        
        result = await self.process_command_async(command)
        return self._parse_ticket_response(result)

    async def close_ticket_as_user(self, ticket_id: str) -> None:
        """
        Close ticket as a user.
        
        Args:
            ticket_id: The Ticket ID to be closed
        """
        ticket_data = {
            "id": ticket_id,
            "status": "ClosedClient"
        }
        
        command = self.create_set_command("/tickets/change-status", ticket_data)
        command.to = self._desk_node
        
        await self.process_command_async(command)

    async def close_ticket_as_user_without_redirect(self, ticket_id: str) -> None:
        """
        Close ticket as a user without Desk sending closed ticket redirect message to builder.
        
        Args:
            ticket_id: The Ticket ID to be closed
        """
        ticket_data = {
            "id": ticket_id,
            "status": "ClosedClient"
        }
        
        command = self.create_set_command("/tickets/change-status-without-redirect", ticket_data)
        command.to = self._desk_node
        
        await self.process_command_async(command)

    async def get_user_open_tickets_async(self, customer_identity: Identity) -> Optional[Ticket]:
        """
        Get user open ticket if any.
        
        Args:
            customer_identity: The customer identity
            
        Returns:
            Optional[Ticket]: The open ticket if exists
        """
        filter_query = quote(f"customerIdentity eq '{customer_identity}' and status eq 'Open'", safe='')
        uri = f"/tickets?$filter={filter_query}"
        
        command = self.create_get_command(uri)
        command.to = self._desk_node
        
        result = await self.process_command_async(command)
        return self._parse_ticket_collection_response(result)

    async def get_customer_active_ticket_async(self, customer_identity: Identity) -> Optional[Ticket]:
        """
        Get customer active ticket.
        
        Args:
            customer_identity: The customer identity
            
        Returns:
            Optional[Ticket]: The active ticket if exists
        """
        filter_query = quote(
            f"customerIdentity eq '{customer_identity}' and (status eq 'Open' or status eq 'Waiting' or status eq 'Assigned')", 
            safe=''
        )
        uri = f"/tickets?$filter={filter_query}"
        
        command = self.create_get_command(uri)
        command.to = self._desk_node
        
        result = await self.process_command_async(command)
        return self._parse_ticket_collection_response(result)

    def _parse_ticket_response(self, result: Command) -> Ticket:
        """Parse ticket from command response."""
        if result.resource and isinstance(result.resource, dict):
            return Ticket(
                id=result.resource.get('id'),
                status=result.resource.get('status'),
                customer_identity=result.resource.get('customerIdentity'),
                agent_identity=result.resource.get('agentIdentity'),
                context=result.resource.get('context')
            )
        return None

    def _parse_ticket_collection_response(self, result: Command) -> Optional[Ticket]:
        """Parse ticket collection and return first ticket."""
        if result.resource and isinstance(result.resource, dict):
            items = result.resource.get('items', [])
            if items:
                first_item = items[0]
                return Ticket(
                    id=first_item.get('id'),
                    status=first_item.get('status'),
                    customer_identity=first_item.get('customerIdentity'),
                    agent_identity=first_item.get('agentIdentity'),
                    context=first_item.get('context')
                )
        return None