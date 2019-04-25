import os

LANGUAGES = []
CONFIG = {
    'have_plantuml': False,
    'have_pathconverter': False,
}


def get_renderer(filename):
    _, ext = os.path.splitext(filename)
    for extensions, renderer in LANGUAGES:
        if ext in extensions:
            return renderer


def can_render(filename):
    return get_renderer(filename) is not None


def render(filename, base_url, content=None):
    if content is None:
        content = open(filename).read()

    return get_renderer(filename)(content, base_url)


def _load_markdown():
    try:
        import markdown
    except ImportError:
        return

    try:
        import plantuml_markdown
    except ImportError:
        pass
    else:
        if os.environ.get('PLANTUML_SERVER'):
            CONFIG['have_plantuml'] = True
        else:
            print("WARNING: PlantUML found but 'PLANTUML_SERVER' environment" +
                  "variable not set. Not using PlantUML.")

    try:
        import pymdownx.pathconverter
    except ImportError:
        pass
    else:
        CONFIG['have_pathconverter'] = True

    def render_markdown(content, base_url=None):
        extensions = ['toc', 'extra']

        if CONFIG['have_plantuml']:
            extensions.append(plantuml_markdown.PlantUMLMarkdownExtension(
                server=os.environ.get('PLANTUML_SERVER')
            ))

        if CONFIG['have_pathconverter']:
            if not base_url.endswith('/'):
                base_url = base_url + '/'
            extensions.append(pymdownx.pathconverter.PathConverterExtension(
                base_path=base_url,
                absolute=True,
            ))

        return markdown.markdown(content, extensions=extensions)

    LANGUAGES.append((['.md', '.mkdn', '.mdwn', '.markdown'], render_markdown))


def _load_restructured_text():
    try:
        from docutils.core import publish_parts
        from docutils.writers.html4css1 import Writer
    except ImportError:
        return

    def render_rest(content, base_url):
        # start by h2 and ignore invalid directives and so on
        # (most likely from Sphinx)
        #
        # base_url is accepted for compatibility with other render_*
        # functions but not used
        #pylint: disable=unused-argument
        settings = {'initial_header_level': 2, 'report_level': 0}
        return publish_parts(content,
                             writer=Writer(),
                             settings_overrides=settings).get('html_body')

    LANGUAGES.append((['.rst', '.rest'], render_rest))


for loader in [_load_markdown, _load_restructured_text]:
    loader()
