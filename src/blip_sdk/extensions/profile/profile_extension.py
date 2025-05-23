from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional

from lime_python import Command, Document
from ..extension_base import ExtensionBase

if TYPE_CHECKING:
    from ...client import Client

PROFILE_URI = "/profile"
GET_STARTED_ID = "get-started"
PERSISTENT_MENU_ID = "persistent-menu"
GREETING_ID = "greeting"


class PlainText:
    """Represents plain text content."""
    
    def __init__(self, text: str = None):
        self.text = text


class DocumentSelect:
    """Represents a document select content."""
    
    def __init__(self, header: Dict = None, options: list = None, scope: str = None):
        self.header = header
        self.options = options or []
        self.scope = scope


class ProfileExtension(ExtensionBase):
    """
    Provides profile management functionality for chatbots.
    """

    def __init__(self, client: Client, to: str = None) -> None:
        super().__init__(client, to)

    async def get_get_started_async(self) -> Optional[Document]:
        """
        Gets the get started configuration.
        
        Returns:
            Document: The get started document
        """
        command = self.create_get_command(f"{PROFILE_URI}/{GET_STARTED_ID}")
        result = await self.process_command_async(command)
        return self._parse_document_response(result)

    async def set_get_started_async(self, get_started: Document) -> Optional[Document]:
        """
        Sets the get started configuration.
        
        Args:
            get_started: The get started document
            
        Returns:
            Document: The response document
        """
        command = self.create_set_command(f"{PROFILE_URI}/{GET_STARTED_ID}", get_started)
        result = await self.process_command_async(command)
        return self._parse_document_response(result)

    async def delete_get_started_async(self) -> Optional[Document]:
        """
        Deletes the get started configuration.
        
        Returns:
            Document: The response document
        """
        command = self.create_delete_command(f"{PROFILE_URI}/{GET_STARTED_ID}")
        result = await self.process_command_async(command)
        return self._parse_document_response(result)

    async def get_greeting_async(self) -> Optional[PlainText]:
        """
        Gets the greeting configuration.
        
        Returns:
            PlainText: The greeting text
        """
        command = self.create_get_command(f"{PROFILE_URI}/{GREETING_ID}")
        result = await self.process_command_async(command)
        return self._parse_plain_text_response(result)

    async def set_greeting_async(self, greeting: PlainText) -> Optional[Document]:
        """
        Sets the greeting configuration.
        
        Args:
            greeting: The greeting text
            
        Returns:
            Document: The response document
        """
        greeting_data = {"text": greeting.text} if hasattr(greeting, 'text') else greeting
        command = self.create_set_command(f"{PROFILE_URI}/{GREETING_ID}", greeting_data)
        result = await self.process_command_async(command)
        return self._parse_document_response(result)

    async def delete_greeting_async(self) -> Optional[PlainText]:
        """
        Deletes the greeting configuration.
        
        Returns:
            PlainText: The response
        """
        command = self.create_delete_command(f"{PROFILE_URI}/{GREETING_ID}")
        result = await self.process_command_async(command)
        return self._parse_plain_text_response(result)

    async def get_persistent_menu_async(self) -> Optional[DocumentSelect]:
        """
        Gets the persistent menu configuration.
        
        Returns:
            DocumentSelect: The persistent menu
        """
        command = self.create_get_command(f"{PROFILE_URI}/{PERSISTENT_MENU_ID}")
        result = await self.process_command_async(command)
        return self._parse_document_select_response(result)

    async def set_persistent_menu_async(self, persistent_menu: DocumentSelect) -> Optional[Document]:
        """
        Sets the persistent menu configuration.
        
        Args:
            persistent_menu: The persistent menu
            
        Returns:
            Document: The response document
        """
        menu_data = {
            "header": persistent_menu.header,
            "options": persistent_menu.options,
            "scope": persistent_menu.scope
        } if hasattr(persistent_menu, 'header') else persistent_menu
        
        command = self.create_set_command(f"{PROFILE_URI}/{PERSISTENT_MENU_ID}", menu_data)
        result = await self.process_command_async(command)
        return self._parse_document_response(result)

    async def delete_persistent_menu_async(self) -> None:
        """
        Deletes the persistent menu configuration.
        """
        command = self.create_delete_command(f"{PROFILE_URI}/{PERSISTENT_MENU_ID}")
        await self.process_command_async(command)

    def _parse_document_response(self, result: Command) -> Optional[Document]:
        """Parse document from command response."""
        if result.resource:
            return result.resource
        return None

    def _parse_plain_text_response(self, result: Command) -> Optional[PlainText]:
        """Parse plain text from command response."""
        if result.resource and isinstance(result.resource, dict):
            text = result.resource.get('text')
            if text:
                return PlainText(text)
        elif isinstance(result.resource, str):
            return PlainText(result.resource)
        return None

    def _parse_document_select_response(self, result: Command) -> Optional[DocumentSelect]:
        """Parse document select from command response."""
        if result.resource and isinstance(result.resource, dict):
            return DocumentSelect(
                header=result.resource.get('header'),
                options=result.resource.get('options', []),
                scope=result.resource.get('scope')
            )
        return None

    async def process_command_async(self, command: Command) -> Command:
        """
        Override to handle GET not found errors gracefully.
        """
        try:
            return await super().process_command_async(command)
        except Exception as e:
            # For GET commands that result in "not found", return empty response
            if (command.method == "get" and 
                "not found" in str(e).lower() or "404" in str(e)):
                # Return a command with empty resource
                return Command(command.method, command.uri, resource=None)
            raise