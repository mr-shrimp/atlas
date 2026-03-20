from jinja2 import Environment, FileSystemLoader

from infrastructure.logging import get_logger

env = Environment(loader=FileSystemLoader("communications/templates/email"))

logger = get_logger(__name__)


def render_template(template_name: str, context: dict):
    """Renders a Jinja2 template using the provided context.

    Loads the specified template from the configured FileSystemLoader
    and renders it with the supplied context dictionary.

    Args:
        template_name (str): The name or relative path of the template file
            within the templates/email directory.
        context (dict): A dictionary containing variables to inject into
            the template during rendering.

    Returns:
        str: The fully rendered template as a string.

    Raises:
        jinja2.exceptions.TemplateNotFound: If the template does not exist.
        jinja2.exceptions.TemplateError: If an error occurs during rendering.
        Exception: Propagates any unexpected exceptions encountered during
            template loading or rendering.
    """
    try:
        template = env.get_template(template_name)
        rendered_template = template.render(**context)
        logger.info("email_template_rendered", template_name=template_name)
        return rendered_template
    except Exception as e:
        logger.error("email_template_render_failure", error=str(e))
        raise
