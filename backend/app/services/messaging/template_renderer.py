import re
from string import Template


class TemplateRenderingError(Exception):
    pass


class TemplateRenderer:
    VARIABLE_PATTERN = re.compile(r"\$\{(\w+)\}")

    @classmethod
    def extract_variables(cls, template_body: str) -> set[str]:
        return set(cls.VARIABLE_PATTERN.findall(template_body))

    @classmethod
    def render(cls, template_body: str, variables: dict | None) -> str:
        variables = variables or {}

        required_vars = cls.extract_variables(template_body)
        provided_vars = set(variables.keys())

        missing = required_vars - provided_vars
        if missing:
            raise TemplateRenderingError(
                f"Missing template variables: {', '.join(sorted(missing))}"
            )

        try:
            return Template(template_body).substitute(variables)
        except KeyError as e:
            raise TemplateRenderingError(f"Missing variable: {e.args[0]}")