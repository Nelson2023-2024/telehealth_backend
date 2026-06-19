import logging
from django.db import models
from typing import TypeVar, Generic, Optional, Type
from django.db.models import QuerySet, Manager

lgr = logging.getLogger(__name__)

T = TypeVar(
    "T", bound=models.Model
)  # T will be some model, I just don't know which one yet


# 1. TypeVar Think of it as a placeholder for a type that gets filled in later.
# 2. Generic Generic[T] is what makes a class accept that placeholder:
# 3. Optional Means the return value is either the thing or None:
# 4. QuerySet Just the proper type hint for what filter() returns:


class ServiceBase(Generic[T]):
    """
    Base service class providing safe CRUD operations.
    All services inherit from this to avoid repeating try/catch logic.
    """

    manager: Manager[T] = None

    def __init__(self, lock_for_update=False, **annotations):
        super(ServiceBase, self).__init__()
        if lock_for_update and self.manager is not None:
            self.manager = self.manager.select_for_update()
        if annotations:
            self.manager = self.manager.annotate(**annotations)

    def _model_name(self):
        """Helper to safely get model name for logging."""
        try:
            return self.manager.model.__name__
        except Exception:
            return "Unknown Model"

    def get(self, *args, active_only: bool = True, **kwargs) -> Optional[T]:
        """
        Get a single record. By default only returns active records
        (is_active=True and state=Active).
        Pass active_only=False to search regardless of status.
        """
        try:
            if self.manager is not None:
                if active_only:
                    kwargs.setdefault("is_active", True)
                    kwargs.setdefault("state__name", "Active")
                return self.manager.get(*args, **kwargs)
        except self.manager.model.DoesNotExist:
            lgr.warning(
                "[%s] Record not found. Filters: %s", self._model_name(), kwargs
            )
        except Exception as e:
            lgr.exception(
                "[%s] GET failed. Filters: %s | Error: %s",
                self._model_name(),
                kwargs,
                str(e),
            )
        return None

    # filter() always returns a QuerySet in Django
    def filter(
        self, *args, active_only: bool = True, **kwargs
    ) -> Optional[QuerySet[T]]:
        """
        Filter records. By default only returns active records
        (is_active=True and state=Active).
        Pass active_only=False to include inactive/disabled records.
        """
        try:
            if self.manager is not None:
                if active_only:
                    kwargs.setdefault("is_active", True)
                    kwargs.setdefault("state__name", "Active")
                return self.manager.filter(*args, **kwargs)
        except Exception as e:
            lgr.exception(
                "[%s] FILTER failed. Filters: %s | Error: %s",
                self._model_name(),
                kwargs,
                str(e),
            )
        return None

    def create(self, **kwargs) -> Optional[T]:
        try:
            if self.manager is not None:
                if "state" not in kwargs and "state_id" not in kwargs:
                    from base.models import State

                    kwargs["state_id"] = State.default_state()
                return self.manager.create(**kwargs)
        except Exception as e:
            lgr.exception(
                "[%s] CREATE failed. Data: %s | Error: %s",
                self._model_name(),
                kwargs,
                str(e),
            )
        return None

    def update(self, pk, **kwargs) -> Optional[T]:
        try:
            record = self.get(id=pk, active_only=False)
            if record is None:
                lgr.warning(
                    "[%s] UPDATE skipped — record not found. PK: %s",
                    self._model_name(),
                    pk,
                )
                return None
            for k, v in kwargs.items():
                setattr(record, k, v)
            record.save()
            record.refresh_from_db()
            return record
        except Exception as e:
            lgr.exception(
                "[%s] UPDATE failed. PK: %s | Data: %s | Error: %s",
                self._model_name(),
                pk,
                kwargs,
                str(e),
            )
        return None

    def delete(self, pk) -> Optional[T]:
        try:
            from base.models import State

            record = self.get(id=pk, active_only=False)
            if record is None:
                lgr.warning(
                    "[%s] DELETE skipped — record not found. PK: %s",
                    self._model_name(),
                    pk,
                )
                return None
            record.is_active = False
            record.state_id = State.disabled_state()
            record.save(update_fields=["is_active", "state"])
            return record
        except Exception as e:
            lgr.exception(
                "[%s] DELETE (soft) failed. PK: %s | Error: %s",
                self._model_name(),
                pk,
                str(e),
            )
        return None
