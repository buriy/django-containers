from django.conf import settings
from django.template import Node
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

    def render(self, context):
        return self.nodelist.render(context)

    def super(self):
        return ''


class ConstantContainerNode(Node):
    def __init__(self, template_path, nodelist):
        try:
            t = get_template(template_path)
            self.template = t
        except:
            if settings.TEMPLATE_DEBUG:
                raise
            self.template = None
        self.nodelist = nodelist

    def render(self, context):
        if self.template:
            context.push()
            
            for part in self.nodelist.get_nodes_by_type(PartNode):
                value = part.render(context)
                context[part.name] = value 

            result = self.template.render(context)
            
            context.pop()
            return result
        else:
            return ''


class ContainerNode(Node):
    def __init__(self, template_name, nodelist):
        self.template_name = Variable(template_name)
        self.nodelist = nodelist

    def render(self, context):
        try:
            template_name = self.template_name.resolve(context)
            t = get_template(template_name)
            
            context.push()
            
            for part in self.nodelist.get_nodes_by_type(PartNode):
                value = part.render(context)
                context[part.name] = value 

            result = t.render(context)
            
            context.pop()
            
            return result
        except TemplateSyntaxError, _e:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''
        except:
            return '' # Fail silently for invalid included templates.

def do_container(parser, token):
    """
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
    nodelist = parser.parse('endcontainer')
    parser.delete_first_token()
    parser.__loaded_parts = parent_loaded_parts 
    
    if path[0] in ('"', "'") and path[-1] == path[0]:
        return ConstantContainerNode(path[1:-1], nodelist)
    return ContainerNode(bits[1], nodelist)
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
