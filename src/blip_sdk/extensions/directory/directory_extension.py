from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import quote

from lime_python import Command, CommandMethod, Node, Identity
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

URI_FORMAT = "lime://{0}/accounts/{1}"
POSTMASTER_FORMAT = "postmaster@{0}"


class Account:
    """Represents an account in the directory."""
    
    def __init__(self, identity: str = None, full_name: str = None, 
                 photo_uri: str = None, inbox_uri: str = None, **kwargs):
        self.identity = identity
        self.full_name = full_name
        self.photo_uri = photo_uri
        self.inbox_uri = inbox_uri
        # Store additional properties
        for key, value in kwargs.items():
            setattr(self, key, value)


class DirectoryExtension(ExtensionBase):
    """
    Provides a service for querying user informations in the public account directory.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)

    async def get_directory_account_async(self, identity: Identity) -> Account:
        """
        Gets an account information from the directory.
        
        Args:
            identity: The identity to query
            
        Returns:
            Account: The account information
            
        Raises:
            ValueError: If identity is None or domain is invalid
        """
        if not identity:
            raise ValueError("identity cannot be null")
        if not identity.domain or identity.domain.isspace():
            raise ValueError("Invalid identity domain")

        uri = URI_FORMAT.format(identity.domain, quote(identity.name, safe=''))
        to_node = Node.parse(POSTMASTER_FORMAT.format(identity.domain))
        
        command = self.create_get_command(uri)
        command.to = to_node
        
        result = await self.process_command_async(command)
        return self._parse_account_response(result)

    def _parse_account_response(self, result: Command) -> Account:
        """Parse account from command response."""
        if result.resource and isinstance(result.resource, dict):
            return Account(
                identity=result.resource.get('identity'),
                full_name=result.resource.get('fullName'),
                photo_uri=result.resource.get('photoUri'),
                inbox_uri=result.resource.get('inboxUri'),
                **{k: v for k, v in result.resource.items() 
                   if k not in ['identity', 'fullName', 'photoUri', 'inboxUri']}
            )
        return None