from lintel.integrations.langchain.base_runnable import BaseRunnable
from lintel.validator_base import FailResult, Validator
from lintel.errors import ValidationError


class ValidatorRunnable(BaseRunnable):
    validator: Validator

    def __init__(self, validator: Validator):
        self.name = validator.rail_alias
        self.validator = validator

    def _validate(self, input: str) -> str:
        response = self.validator.validate(input, self.validator._metadata)
        if isinstance(response, FailResult):
            raise ValidationError(
                (
                    "The response from the LLM failed validation!"
                    f" {response.error_message}"
                )
            )
        return input
