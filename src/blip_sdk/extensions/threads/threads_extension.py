from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional, List

from lime_python import Command, Node, Identity
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

DEFAULT_THREADS_DOMAIN = "threads.msging.net"
POSTMASTER = "postmaster"


class Thread:
    """Represents a conversation thread."""
    
    def __init__(self, id: str = None, owner_identity: str = None, 
                 participants: List[str] = None, created_date: str = None):
        self.id = id
        self.owner_identity = owner_identity
        self.participants = participants or []
        self.created_date = created_date


class ThreadsExtension(ExtensionBase):
    """
    Provides thread management functionality for group conversations.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)
        self._threads_address = Node(POSTMASTER, DEFAULT_THREADS_DOMAIN, None)

    async def create_thread_async(self, participants: List[Identity]) -> Thread:
        """
        Create a new conversation thread.
        
        Args:
            participants: List of participant identities
            
        Returns:
            Thread: The created thread
        """
        if not participants:
            raise ValueError("participants cannot be null or empty")

        thread_data = {
            "participants": [str(p) for p in participants]
        }

        command = self.create_set_command("/threads", thread_data)
        command.to = self._threads_address
        
        result = await self.process_command_async(command)
        return self._parse_thread_response(result)

    async def get_thread_async(self, thread_id: str) -> Thread:
        """
        Get a thread by ID.
        
        Args:
            thread_id: The thread ID
            
        Returns:
            Thread: The thread information
        """
        if not thread_id:
            raise ValueError("threadId cannot be null or empty")

        command = self.create_get_command(f"/threads/{thread_id}")
        command.to = self._threads_address
        
        result = await self.process_command_async(command)
        return self._parse_thread_response(result)

    async def get_threads_async(self, skip: int = 0, take: int = 100) -> List[Thread]:
        """
        Get list of threads.
        
        Args:
            skip: Number of items to skip
            take: Number of items to take
            
        Returns:
            List[Thread]: List of threads
        """
        uri = f"/threads?$skip={skip}&$take={take}"
        command = self.create_get_command(uri)
        command.to = self._threads_address
        
        result = await self.process_command_async(command)
        return self._parse_threads_collection_response(result)

    async def add_participant_async(self, thread_id: str, participant: Identity) -> None:
        """
        Add a participant to a thread.
        
        Args:
            thread_id: The thread ID
            participant: The participant identity to add
        """
        if not thread_id:
            raise ValueError("threadId cannot be null or empty")
        if not participant:
            raise ValueError("participant cannot be null")

        participant_data = {
            "value": str(participant)
        }

        command = self.create_set_command(f"/threads/{thread_id}/participants", participant_data)
        command.to = self._threads_address
        
        await self.process_command_async(command)

    async def remove_participant_async(self, thread_id: str, participant: Identity) -> None:
        """
        Remove a participant from a thread.
        
        Args:
            thread_id: The thread ID
            participant: The participant identity to remove
        """
        if not thread_id:
            raise ValueError("threadId cannot be null or empty")
        if not participant:
            raise ValueError("participant cannot be null")

        command = self.create_delete_command(f"/threads/{thread_id}/participants/{participant}")
        command.to = self._threads_address
        
        await self.process_command_async(command)

    async def delete_thread_async(self, thread_id: str) -> None:
        """
        Delete a thread.
        
        Args:
            thread_id: The thread ID to delete
        """
        if not thread_id:
            raise ValueError("threadId cannot be null or empty")

        command = self.create_delete_command(f"/threads/{thread_id}")
        command.to = self._threads_address
        
        await self.process_command_async(command)

    def _parse_thread_response(self, result: Command) -> Thread:
        """Parse thread from command response."""
        if result.resource and isinstance(result.resource, dict):
            return Thread(
                id=result.resource.get('id'),
                owner_identity=result.resource.get('ownerIdentity'),
                participants=result.resource.get('participants', []),
                created_date=result.resource.get('createdDate')
            )
        return None

    def _parse_threads_collection_response(self, result: Command) -> List[Thread]:
        """Parse threads collection from command response."""
        threads = []
        if result.resource and isinstance(result.resource, dict):
            items = result.resource.get('items', [])
            for item in items:
                thread = Thread(
                    id=item.get('id'),
                    owner_identity=item.get('ownerIdentity'),
                    participants=item.get('participants', []),
                    created_date=item.get('createdDate')
                )
                threads.append(thread)
        return threads