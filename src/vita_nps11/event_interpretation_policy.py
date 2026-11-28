
"""Explicit role-dependent interpretation rules for world events.

The policy converts an objective event and a participant role into
one character-specific perception and one consequence proposal.

Rules are deterministic and explicit. The policy never copies the
full objective event description into a character's perception.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping

from vita_nps11.domain.events import ParticipantRole
from vita_nps11.domain.perception import PerceptionSource


class UnknownEventInterpretationError(KeyError):
    """Raised when an event type and participant role have no rule."""


class AmbiguousInterpretationTargetError(ValueError):
    """Raised when a rule's target role does not identify one character."""


@dataclass(frozen=True, slots=True)
class EventInterpretationRule:
    """One explicit interpretation rule for an event type and role."""

    event_type: str
    role: ParticipantRole
    perception_source: PerceptionSource
    perception_summary: str
    consequence_type: str
    consequence_description: str
    strength: float = 1.0
    salience: float = 0.8
    confidence: float = 0.9
    context_tags: tuple[str, ...] = ()
    target_role: ParticipantRole | None = None

    def __post_init__(self) -> None:
        for name in (
            "event_type",
            "perception_summary",
            "consequence_type",
            "consequence_description",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        if not isinstance(self.role, ParticipantRole):
            raise TypeError("role must be a ParticipantRole")

        if not isinstance(self.perception_source, PerceptionSource):
            raise TypeError(
                "perception_source must be a PerceptionSource"
            )

        if self.target_role is not None:
            if not isinstance(self.target_role, ParticipantRole):
                raise TypeError(
                    "target_role must be a ParticipantRole or None"
                )
            if self.target_role is self.role:
                raise ValueError(
                    "target_role cannot be the rule's own participant role"
                )

        for name in ("strength", "salience", "confidence"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(
                value, (int, float)
            ):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within [0, 1]")

        if not isinstance(self.context_tags, tuple):
            raise TypeError("context_tags must be a tuple")

        for tag in self.context_tags:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError(
                    "context_tags must contain non-empty strings"
                )

        object.__setattr__(
            self,
            "context_tags",
            tuple(sorted({tag.strip().casefold() for tag in self.context_tags})),
        )


class EventInterpretationPolicy:
    """Immutable lookup of event-and-role interpretation rules."""

    def __init__(
        self,
        rules: Iterable[EventInterpretationRule],
    ) -> None:
        validated: dict[
            tuple[str, ParticipantRole],
            EventInterpretationRule,
        ] = {}

        for rule in rules:
            if not isinstance(rule, EventInterpretationRule):
                raise TypeError(
                    "rules must contain EventInterpretationRule objects"
                )

            key = (rule.event_type, rule.role)
            if key in validated:
                raise ValueError(
                    f"duplicate interpretation rule: "
                    f"{rule.event_type}/{rule.role.value}"
                )

            validated[key] = rule

        self._rules: Mapping[
            tuple[str, ParticipantRole],
            EventInterpretationRule,
        ] = MappingProxyType(validated)

    def resolve(
        self,
        event_type: str,
        role: ParticipantRole,
    ) -> EventInterpretationRule:
        """Return the exact rule for an event type and participant role."""

        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")

        if not isinstance(role, ParticipantRole):
            raise TypeError("role must be a ParticipantRole")

        rule = self._rules.get((event_type, role))
        if rule is None:
            raise UnknownEventInterpretationError(
                f"no interpretation rule for "
                f"{event_type!r}/{role.value!r}"
            )

        return rule

    @property
    def supported_event_types(self) -> tuple[str, ...]:
        """Return event types covered by at least one rule."""

        return tuple(sorted({key[0] for key in self._rules}))


def create_betrayal_policy() -> EventInterpretationPolicy:
    """Create the initial deterministic betrayal interpretation policy.

    These are prototype rules for testing the runtime, not universal
    psychological assumptions.
    """

    return EventInterpretationPolicy(
        rules=(
            EventInterpretationRule(
                event_type="betrayal",
                role=ParticipantRole.VICTIM,
                perception_source=PerceptionSource.DIRECT,
                perception_summary=(
                    "You were directly involved in an event "
                    "classified as a betrayal."
                ),
                consequence_type="betrayal_trust_breach",
                consequence_description=(
                    "The character experienced a direct breach of trust "
                    "involving the identified perpetrator."
                ),
                strength=0.8,
                salience=0.95,
                confidence=0.95,
                context_tags=("betrayal", "trust", "personal"),
                target_role=ParticipantRole.PERPETRATOR,
            ),
            EventInterpretationRule(
                event_type="betrayal",
                role=ParticipantRole.PERPETRATOR,
                perception_source=PerceptionSource.DIRECT,
                perception_summary=(
                    "You were directly involved in an action "
                    "classified as a betrayal."
                ),
                consequence_type="betrayal_responsibility",
                consequence_description=(
                    "The character is recorded as the perpetrator "
                    "of the betrayal event."
                ),
                strength=0.8,
                salience=0.8,
                confidence=1.0,
                context_tags=("betrayal", "responsibility"),
            ),
            EventInterpretationRule(
                event_type="betrayal",
                role=ParticipantRole.WITNESS,
                perception_source=PerceptionSource.WITNESSED,
                perception_summary=(
                    "You witnessed an interaction classified "
                    "as a betrayal involving other participants."
                ),
                consequence_type="betrayal_witnessed",
                consequence_description=(
                    "The character witnessed a betrayal involving "
                    "the identified perpetrator."
                ),
                strength=0.6,
                salience=0.7,
                confidence=0.85,
                context_tags=("betrayal", "witness", "social"),
                target_role=ParticipantRole.PERPETRATOR,
            ),
        )
    )
