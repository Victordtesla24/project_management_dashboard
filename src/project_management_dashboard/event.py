"""Event system for database operations."""
from typing import Any, TypeVar

T = TypeVar("T")


class Event:
    """Base event class."""

    def __init__(self, target: Any) -> None:
        self.target = target
        self.propagate = True


class DDLEvent(Event):
    """Event for DDL operations."""


class DMLEvent(Event):
    """Event for DML operations."""


class SchemaEvent(DDLEvent):
    """Event for schema operations."""


class TableEvent(SchemaEvent):
    """Event for table operations."""


class ColumnEvent(SchemaEvent):
    """Event for column operations."""


class ConstraintEvent(SchemaEvent):
    """Event for constraint operations."""


class IndexEvent(SchemaEvent):
    """Event for index operations."""


class ViewEvent(SchemaEvent):
    """Event for view operations."""


class SequenceEvent(SchemaEvent):
    """Event for sequence operations."""


class TriggerEvent(SchemaEvent):
    """Event for trigger operations."""


class FunctionEvent(SchemaEvent):
    """Event for function operations."""


class ProcedureEvent(SchemaEvent):
    """Event for procedure operations."""


class PackageEvent(SchemaEvent):
    """Event for package operations."""


class TypeEvent(SchemaEvent):
    """Event for type operations."""


class SynonymEvent(SchemaEvent):
    """Event for synonym operations."""


class GrantEvent(SchemaEvent):
    """Event for grant operations."""


class RevokeEvent(SchemaEvent):
    """Event for revoke operations."""


class CommentEvent(SchemaEvent):
    """Event for comment operations."""


class AlterEvent(SchemaEvent):
    """Event for alter operations."""


class CreateEvent(SchemaEvent):
    """Event for create operations."""


class DropEvent(SchemaEvent):
    """Event for drop operations."""


class RenameEvent(SchemaEvent):
    """Event for rename operations."""


class TruncateEvent(SchemaEvent):
    """Event for truncate operations."""


class InsertEvent(DMLEvent):
    """Event for insert operations."""


class UpdateEvent(DMLEvent):
    """Event for update operations."""


class DeleteEvent(DMLEvent):
    """Event for delete operations."""


class SelectEvent(DMLEvent):
    """Event for select operations."""


class MergeEvent(DMLEvent):
    """Event for merge operations."""


class CallEvent(DMLEvent):
    """Event for call operations."""


class ExecuteEvent(DMLEvent):
    """Event for execute operations."""


class BeginEvent(DMLEvent):
    """Event for begin operations."""


class CommitEvent(DMLEvent):
    """Event for commit operations."""


class RollbackEvent(DMLEvent):
    """Event for rollback operations."""


class SavepointEvent(DMLEvent):
    """Event for savepoint operations."""


class RollbackToEvent(DMLEvent):
    """Event for rollback to operations."""


class LockEvent(DMLEvent):
    """Event for lock operations."""


class UnlockEvent(DMLEvent):
    """Event for unlock operations."""


class ExplainEvent(DMLEvent):
    """Event for explain operations."""


class AnalyzeEvent(DMLEvent):
    """Event for analyze operations."""


class VacuumEvent(DMLEvent):
    """Event for vacuum operations."""


class ClusterEvent(DMLEvent):
    """Event for cluster operations."""


class ReindexEvent(DMLEvent):
    """Event for reindex operations."""


class CheckpointEvent(DMLEvent):
    """Event for checkpoint operations."""


class SetEvent(DMLEvent):
    """Event for set operations."""


class ShowEvent(DMLEvent):
    """Event for show operations."""


class UseEvent(DMLEvent):
    """Event for use operations."""


class PrepareEvent(DMLEvent):
    """Event for prepare operations."""


class DeallocateEvent(DMLEvent):
    """Event for deallocate operations."""


class ExecuteStatementEvent(DMLEvent):
    """Event for execute statement operations."""


class FetchEvent(DMLEvent):
    """Event for fetch operations."""


class MoveEvent(DMLEvent):
    """Event for move operations."""


class CloseEvent(DMLEvent):
    """Event for close operations."""


class ListenEvent(DMLEvent):
    """Event for listen operations."""


class NotifyEvent(DMLEvent):
    """Event for notify operations."""


class UnlistenEvent(DMLEvent):
    """Event for unlisten operations."""


class LoadEvent(DMLEvent):
    """Event for load operations."""


class CopyEvent(DMLEvent):
    """Event for copy operations."""


class EndEvent(DMLEvent):
    """Event for end operations."""


class DisconnectEvent(DMLEvent):
    """Event for disconnect operations."""


class ResetEvent(DMLEvent):
    """Event for reset operations."""
