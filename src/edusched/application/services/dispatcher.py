"""命令和查询分发器。

负责将命令和查询分发到相应的处理器。
"""

import logging
from typing import Any, Dict, Type, TypeVar, Union

from ..base import (
    BaseCommand, BaseQuery, CommandResult, QueryResult,
    ICommandHandler, IQueryHandler
)

logger = logging.getLogger(__name__)

C = TypeVar("C", bound=BaseCommand)
Q = TypeVar("Q", bound=BaseQuery)
T = TypeVar("T")


class CommandDispatcher:
    """命令分发器。"""

    def __init__(self):
        self._handlers: Dict[Type[BaseCommand], ICommandHandler] = {}

    def register_handler(
        self,
        command_type: Type[C],
        handler: ICommandHandler[C, T]
    ) -> None:
        """注册命令处理器。"""
        self._handlers[command_type] = handler
        logger.debug(f"Registered handler for command: {command_type.__name__}")

    async def dispatch(self, command: BaseCommand) -> CommandResult[Any]:
        """分发命令到对应的处理器。"""
        command_type = type(command)
        handler = self._handlers.get(command_type)

        if not handler:
            error_msg = f"No handler registered for command: {command_type.__name__}"
            logger.error(error_msg)
            return CommandResult.failure_result(error_msg)

        try:
            logger.debug(f"Dispatching command: {command_type.__name__}")
            result = await handler.handle(command)
            logger.debug(f"Command {command_type.__name__} handled successfully")
            return result

        except Exception as e:
            error_msg = f"Error handling command {command_type.__name__}: {str(e)}"
            logger.exception(error_msg)
            return CommandResult.failure_result(error_msg)


class QueryDispatcher:
    """查询分发器。"""

    def __init__(self):
        self._handlers: Dict[Type[BaseQuery], IQueryHandler] = {}

    def register_handler(
        self,
        query_type: Type[Q],
        handler: IQueryHandler[Q, T]
    ) -> None:
        """注册查询处理器。"""
        self._handlers[query_type] = handler
        logger.debug(f"Registered handler for query: {query_type.__name__}")

    async def dispatch(self, query: BaseQuery) -> QueryResult[Any]:
        """分发查询到对应的处理器。"""
        query_type = type(query)
        handler = self._handlers.get(query_type)

        if not handler:
            error_msg = f"No handler registered for query: {query_type.__name__}"
            logger.error(error_msg)
            return QueryResult(success=False, data=None, total=0, error=error_msg)

        try:
            logger.debug(f"Dispatching query: {query_type.__name__}")
            result = await handler.handle(query)
            logger.debug(f"Query {query_type.__name__} handled successfully")
            return result

        except Exception as e:
            error_msg = f"Error handling query {query_type.__name__}: {str(e)}"
            logger.exception(error_msg)
            return QueryResult(success=False, data=None, total=0, error=error_msg)


class ApplicationServiceDispatcher:
    """应用服务分发器。

    统一分发命令和查询，提供简化的接口。
    """

    def __init__(self):
        self.command_dispatcher = CommandDispatcher()
        self.query_dispatcher = QueryDispatcher()

    def register_command_handler(
        self,
        command_type: Type[C],
        handler: ICommandHandler[C, T]
    ) -> None:
        """注册命令处理器。"""
        self.command_dispatcher.register_handler(command_type, handler)

    def register_query_handler(
        self,
        query_type: Type[Q],
        handler: IQueryHandler[Q, T]
    ) -> None:
        """注册查询处理器。"""
        self.query_dispatcher.register_handler(query_type, handler)

    async def send_command(self, command: BaseCommand) -> CommandResult[Any]:
        """发送命令。"""
        return await self.command_dispatcher.dispatch(command)

    async def send_query(self, query: BaseQuery) -> QueryResult[Any]:
        """发送查询。"""
        return await self.query_dispatcher.dispatch(query)