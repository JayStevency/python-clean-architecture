# -*- coding: utf-8 -*-
import abc
from dataclasses import dataclass
import typing as t

from pca.utils.functools import reify

from .dependency_injection import Container
from .logic import UseCaseError, ValidationError
from .schemas import Schema


class LogicError(Exception):
    """
    Base class for an error indicating
    """


@dataclass(frozen=True)
class UseCaseInterface:
    """
    Describes a variant of interaction with the use-case and its validation.
    Used by application environment to construct ie. form of input controls.
    """
    action: str
    schema: t.Optional[Schema]


InputMapping = t.Mapping[str, t.Any]


@dataclass(frozen=True)
class UseCaseInput:
    """
    Data Transfer Object of describing UseCase invocation.
    `action` is optional when there is only one action to choose.
    `data` is optional when the request is pre-invocation test to
        check availability of the action to execute.
    """
    action: t.Optional[str] = None
    data: t.Optional[InputMapping] = None

    def __getattr__(self, item):
        return self.data and self.data.get(item)


@dataclass(frozen=True)
class UseCaseResult:
    data: InputMapping = frozendict()
    errors: t.Mapping[str, UseCaseError] = frozendict()

    @property
    def is_success(self):
        return not self.errors


class AbstractUseCase(metaclass=abc.ABCMeta):
    """
    This is core object of the application. Its methods represent
    application-specific actions that can be taken or queries to ask.
    """
    Input: t.ClassVar[UseCaseInput]
    container: Container

    @property
    @abc.abstractmethod
    def interfaces(self) -> t.List[UseCaseInterface]:
        """
        List of all descriptions of interfaces for all states of the use-case's
        process and their actions.
        """

    @abc.abstractmethod
    def invoke(self, input: UseCaseInput) -> UseCaseResult:
        """
        Main entry point into the UseCase.
        """
        if not self.is_available(input):  # TODO ToCToU problem?
            raise LogicError
        validated_data = self.validate(input)
        return self.execute(input.action, validated_data)

    def is_available(self, input: t.Optional[UseCaseInput]):
        """
        A hook for definition of pre-validation conditions to invoke
        processing of the UseCase. The second role is to use this definition
        to pre-invocation check whether it's reasonable to invoke.

        True by default.
        """
        return True

    @abc.abstractmethod
    def validate(self, input: UseCaseInput) -> InputMapping:
        """A hook for making a validation of a kind you like."""

    @abc.abstractmethod
    def execute(self, action: t.Optional[str], input: InputMapping) -> UseCaseResult:
        """A hook for the main point of execution data already validated."""


# noinspection PyAbstractClass
class SimpleUseCase(AbstractUseCase):
    Schema: t.Optional[t.ClassVar[Schema]] = None

    def __init__(self, container: Container):
        self.container = container

    @reify
    def interfaces(self) -> t.List[UseCaseInterface]:
        return [UseCaseInterface(schema=self.schema_class, action='action')]

    def validate(self, input: UseCaseInput) -> InputMapping:
        context = self.get_context()
        schema = self.Schema(context=context)
        return schema.load(input.data)

    def execute(self, action: t.Optional[str], input: InputMapping) -> UseCaseResult:
        return UseCaseResult(errors={}, data=result)

    def get_context(self) -> dict:
        raise NotImplementedError
