from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional
from lime_python import Command

from ..extension_base import ExtensionBase
from .content_types import ContentTypes
from .uri_templates import UriTemplates

if TYPE_CHECKING:
    from ...client import Client

POSTMASTER_ANALYTICS = 'postmaster@analytics.msging.net'


class EventTrackerExtension(ExtensionBase):
    """Extension to handle BLiP event tracking analytics."""

    def __init__(self, client: Client) -> None:
        """Initialize a new instance of EventTrackerExtension.

        Args:
            client (Client): The BLiP client.
        """
        super().__init__(client, POSTMASTER_ANALYTICS)

    async def track_async(
        self,
        category: str,
        action: str,
        identity: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None
    ) -> Command:
        """Track an event with the provided information.

        Args:
            category (str): The event category.
            action (str): The event action.
            identity (Optional[str], optional): The user identity. Defaults to None.
            extras (Optional[Dict[str, Any]], optional): Additional information about the event. Defaults to None.

        Returns:
            Command: Command response.
        """
        if not category:
            raise ValueError('The category is required')
        if not action:
            raise ValueError('The action is required')

        track_resource = {
            'category': category,
            'action': action,
            'extras': extras
        }

        if identity is not None:
            track_resource['identity'] = identity

        track_command = self.create_set_command(
            UriTemplates.EVENTS,
            track_resource,
            ContentTypes.EVENT
        )

        return await self.process_command_async(track_command)

    async def get_categories_async(
        self,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        **kwargs
    ) -> Command:
        """Get all event categories.

        Args:
            skip (Optional[int], optional): Number of categories to skip. Defaults to None.
            take (Optional[int], optional): Number of categories to take. Defaults to None.
            kwargs: Any other optional parameter not covered by the method.

        Returns:
            Command: Command response with categories.
        """
        return await self.process_command_async(
            self.create_get_command(
                self.build_resource_query(
                    UriTemplates.EVENTS,
                    {
                        '$skip': skip,
                        '$take': take,
                        **kwargs
                    }
                )
            )
        )

    async def get_actions_async(
        self,
        category: str,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> Command:
        """Get actions for a specific category.

        Args:
            category (str): The event category name.
            skip (Optional[int], optional): Number of actions to skip. Defaults to None.
            take (Optional[int], optional): Number of actions to take. Defaults to None.
            start_date (Optional[str], optional): Filter actions from this date. Defaults to None.
            end_date (Optional[str], optional): Filter actions until this date. Defaults to None.
            kwargs: Any other optional parameter not covered by the method.

        Returns:
            Command: Command response with actions.
        """
        if not category:
            raise ValueError('The category is required')

        return await self.process_command_async(
            self.create_get_command(
                self.build_resource_query(
                    self.build_uri(UriTemplates.EVENTS_CATEGORY, category),
                    {
                        '$skip': skip,
                        '$take': take,
                        'startDate': start_date,
                        'endDate': end_date,
                        **kwargs
                    }
                )
            )
        )