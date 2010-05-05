from django.template import Template
from django.template.context import Context

var = "{{ left }} {{ left_inner }} {{ text }} {{ right_inner }} {{ right }}"
template = """
{% render var left_inner="this" right_inner="the"|striptags %}
    {# Hi #} is {# content! #}
    {% part left %}Hi,{% endpart %}
    {% part right %}content!{% endpart %}
{% endrender %}
"""

expected = "Hi, this is the content!"

scheme = Template(var, None, "included.html")
const = Template(template.strip(), None, "parent.html")
produced = const.render(Context({'var': scheme}))
assert produced == expected, "Test failed! Got: '%s'" % produced