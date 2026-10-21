from jinja2 import Environment, FileSystemLoader, select_autoescape


class Template:
    """A template object.

    :param template: The filename of the template to render, relative to the
                    configured template directory.
    :param kwargs: any additional options to be passed to the Jinja
                   environment's ``get_template()`` method.
    """
    #: The Jinja environment. The ``initialize()`` method must be called before
    #: this attribute is accessed.
    jinja_env = None

    @classmethod
    def initialize(cls, template_dir='templates', enable_async=False,
                   **kwargs):
        """Initialize the templating subsystem.

        This method is automatically invoked when the first template is
        created. The application can call it explicitly if custom options need
        to be provided.

        :param template_dir: the directory where templates are stored. This
                             argument is optional. The default is to load
                 