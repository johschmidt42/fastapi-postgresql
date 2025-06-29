from pydantic import (
    BaseModel,
    model_validator,
    ConfigDict,
)


class BasePatch(BaseModel):
    """
    A base Pydantic model for PATCH requests.
    It includes a validator to ensure at least one field is provided in the request
    and sets extra='forbid' by default.
    """

    model_config = {
        "extra": "forbid",
    }

    @model_validator(mode="after")
    def _check_at_least_one_field_is_set(self):
        """
        Validates that at least one field was provided in the request data.
        `self.model_fields_set` contains the names of fields that were explicitly set in the input.
        """
        if not self.model_fields_set:
            # Dynamically create a list of field names for the current model
            field_names: str = ", ".join(
                f"'{field_name}'" for field_name in self.model_fields.keys()
            )

            error_message = f"At least one of the following fields must be provided for an update: {field_names}."

            raise ValueError(error_message)
        return self


class BaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
