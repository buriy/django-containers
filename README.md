Basics
======
"Containers" are html-only widgets for Django.
Invaluable for complex HTML designs.
Powerful replacement for your {% include %} tags!

Examples
========
This example outputs "Hello, world!":
-------------------------------------
    ::sample.html::

    {% load container_tags %}
    {% render "greetings.html" %}
        {% part greetings %}Hello{% endpart %}
        {% part object %}World{% endpart %}
    {% endrender %}

    ::greetings.html::

    ...
    {{ greetings }}, {{ object }}!
    ...

This example renders beautiful css button ::
-------------------------------------
Based on <a href="http://www.oscaralexander.com/tutorials/how-to-make-sexy-buttons-with-css.html">Tutorial on sexy buttons with CSS</a>
Just use css code from the site and the following container:

    ::styles/button.html::

    <a {{ attrs }} class="{% firstof classes "button" %}" href="{{ url }}"
        onclick="this.blur();{{ onclick }}"><span>{{ text }}</span></a>
    
    ::myform.html::
    
    {% load container_tags %}
    {% render "styles/button.html" url=object.get_edit_url %}
    {% trans "Edit this form" %}
    {% part attrs %}id="{{ form.name }}-edit"{% endpart %}
    {% endrender %}

How this works:
All internals between {% render %} and all {% part %} entries are rendered to variables
"content" and "text" (where text = content.strip()). In this example, {{ text }}
variable is used.

Advanced features:
==================

 * Can be installed as builtins (with "import containers.as_builtins" from your urls.py or settings.py)
 * Can use variable template name to render instead of constant.
 * {{ variable }} is rendered empty if that variable is missing.
 * Raises TemplateSyntaxError if any part is used twice.
 * Can use variables from outer context, so you can continue to live with your {% with %}, you lazy bastard! :)
 * "content" and "text", if you have the most important part.
 * Sexy css buttons example included!
