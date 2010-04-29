Basics
======
"Containers" are html-only widgets for Django.
Invaluable for complex HTML designs.

Examples
========
This example outputs "Hello, world!":
-------------------------------------
    ::sample.html::

    {% load container_tags %}
    {% container "greetings.html" %}
        {% part greetings %}Hello{% endpart %}
        {% part object %}World{% endpart %}
    {% endcontainer %}

    ::greetings.html::

    ...
    {{ greetings }}, {{ object }}!
    ...

This example outputs beautiful css buttons ::
-------------------------------------
Based on <a href="http://www.oscaralexander.com/tutorials/how-to-make-sexy-buttons-with-css.html">Tutorial on sexy buttons with CSS</a>
Just use css code from the site and the following container:

    ::styles/button.html::

    <a {{ attrs }} class="{% firstof class 'button' %}" href="{{ href }}"
        onclick="this.blur();{{ onclick }}"><span>{{ name }}</span></a>
    
    ::myform.html::
    
    {% load container_tags %}
    {% container "styles/button.html" %}
    {% part href %}{% block edit-href %}{{ object.get_edit_url }}{% endblock %}{% endpart %}
    {% part name %}{% block edit-name %}{% trans "Edit" %}{% endblock %}{% endpart %}
    {% part attrs %}id="{{ form.name }}-edit"{% endpart %}
    {% endcontainer %}

Advanced features:
==================

 * Can be installed as builtins (with "import containers.as_builtins" from your urls.py)
 * Can use variable template name for container instead of constant.
 * If some part is not defined, variable with that name is used, empty if no such variable exists.
 * Raises TemplateSyntaxError if any part is used twice.
 * Sexy css buttons example included!
