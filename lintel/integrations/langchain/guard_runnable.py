from lintel.integrations.langchain.base_runnable import BaseRunnable
from lintel.guard import Guard
from lintel.errors import ValidationError
from lintel.classes.output_type import OT
from lintel.classes.validation_outcome import ValidationOutcome


class GuardRunnable(BaseRunnable):
    guard: Guard

    def __init__(self, guard: Guard):
        self.name = guard.name
        self.guard = guard

    def _validate(self, input: str) -> OT:
        response: ValidationOutcome[OT] = self.guard.validate(input)
        validated_output = response.validated_output
        if validated_output is None or response.validation_passed is False:
            raise ValidationError(
                (
                    "The response from the LLM failed validation!"
                    "See `guard.history` for more details."
                )
            )
        return validated_output
