from django.conf import settings
from django.template import Node, Template, FilterExpression
from django.template import TemplateSyntaxError
from django.template import Variable
from django.template.loader import get_template
from django.template import Library

register = Library()

class PartNode(Node):
    def __init__(self, name, nodelist):
        self.name, self.nodelist = name, nodelist

    def __repr__(self):
        return "<Part Node: %s. Contents: %r>" % (self.name, self.nodelist)

    def get_nodes_by_type(self, nodetype):
        # we accept Part in part, but get_nodes_by_type
        # should return only the outmost ones
        if issubclass(nodetype, PartNode):
            return self
        return super(PartNode, self).get_nodes_by_type(nodetype)

    def render(self, context):
        return ''

    def render_value(self, context):
        return self.nodelist.render(context)

    def super(self):
        return ''


class ContainerNode(Node):
    def __init__(self, template, nodelist, refs={}):
        self.nodelist, self.refs, self.template = nodelist, refs, template
        if not isinstance(template, (Variable, Template, FilterExpression)):
            # find template right here to speed up error detection
            try:
                self.template = get_template(template)
            except:
                if settings.TEMPLATE_DEBUG:
                    raise
                self.template = None

    def get_template(self, context):
        template = self.template
        if isinstance(template, (Variable, FilterExpression)):
            template = template.resolve(context)
        if not isinstance(template, Template):
            template = get_template(template)
        return template

    def render(self, context):
        try:
            text = self.nodelist.render(context)
            template = self.get_template(context)

            context.push()
            
            context['content'] = text
            context['text'] = text.strip()
            
            for part in self.nodelist.get_nodes_by_type(PartNode):
                value = part.render_value(context)
                context[part.name] = value
            
            for name, value in self.refs.items():
                context[name] = value.resolve(context)

            result = template.render(context)
            
            context.pop()
            
            return result
        except TemplateSyntaxError, _e:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''
        except: #NoneType has no method ...
            if settings.TEMPLATE_DEBUG:
                raise
            return '' # Fail silently for invalid included templates.

def do_container(parser, token):
    """
    Deprecated. Provided only for compatibility with older version.
    Loads a template and renders it with the current context.

    Example::

        {% container "foo/some_include" %}
            {% part left %}Hello{% endpart %}
            {% part right %}World{% endpart %}
        {% endcontainer %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError, "%r tag takes one argument: the name of the template to be included" % bits[0]
    path = bits[1]
    
    parent_loaded_parts = getattr(parser, '__loaded_parts', [])
    parser.__loaded_parts = []
    nodelist = parser.parse(['endcontainer'])
    parser.delete_first_token()
    parser.__loaded_parts = parent_loaded_parts 

    if path[0] in ('"', "'") and path[-1] == path[0]:
        return ContainerNode(path[1:-1], nodelist)
    return ContainerNode(Variable(bits[1]), nodelist)
do_container = register.tag('container', do_container)


def do_part(parser, token):
    """
    Sets value of the container variable.

    For example::

        {% part name %}world{% endpart %}
    """
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "'%s' tag takes only one argument" % bits[0]
    part_name = bits[1]
    # Keep track of the names of BlockNodes found in this template, so we can
    # check for duplication.
    try:
        if part_name in parser.__loaded_parts:
            raise TemplateSyntaxError, "'%s' tag with name '%s' appears more than once" % (bits[0], part_name)
        parser.__loaded_parts.append(part_name)
    except AttributeError: # parser.__loaded_parts isn't a list yet
        raise TemplateSyntaxError, "'%s' tag with name '%s' appears without any container!" % (bits[0], part_name)
    nodelist = parser.parse(('endpart', 'endpart %s' % part_name))
    parser.delete_first_token()
    return PartNode(part_name, nodelist)
do_part = register.tag('part', do_part)


def prepare_refs(parser, bits):
    refs = {}
    for x in bits:
        k, v = x.split('=', 1)
        refs[k] = parser.compile_filter(v)
    return refs


def do_render(parser, token):
    """
    Loads a template and renders it with the current context.

    Example::

        {% render "foo/some_include" left_inner="this" right_inner="the" %}
            {# Hi #} is {# content! #}
            {% part left %}Hi, {% endpart %}
            {% part right %}content!{% endpart %}
        {% endrender %}
        
    with the template 

        {{ left }} {{ left_inner }} {{ text }} {{ right_inner }} {{ right }}
    
    will render
    
        Hi, this is the content!
    
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError, "%r tag is missing the name of the template to be included" % bits[0]
    
    parent_loaded_parts = getattr(parser, '__loaded_parts', [])
    parser.__loaded_parts = []
    nodelist = parser.parse(['endrender'])
    parser.delete_first_token()
    parser.__loaded_parts = parent_loaded_parts 
    
    refs = prepare_refs(parser, bits[2:])
    first = parser.compile_filter(bits[1])
    return ContainerNode(first, nodelist, refs)
do_render = register.tag('render', do_render)
