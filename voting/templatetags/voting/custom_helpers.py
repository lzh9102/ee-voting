from django import template
from django.core.urlresolvers import reverse

register = template.Library()

def strip_quotes(s):
    if s[0] == s[-1] and s.startswith(('"', "'")): # is quoted string
        return s[1:-1] # strip quotes
    else:
        return s

@register.simple_tag(takes_context=True)
def css_active(context, url):
    request = context['request']
    if request.path == url:
        return "active"
    return ""

@register.filter(name='css_class')
def css_class(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.tag(name='navlink')
def do_navlink(parser, token):
    """ usage: {% navlink <view> %} ... {% endnavlink %}

        Generate navigation link for <view>. The navigation link is a listitem
        (<li><a>...</a></li>). If the link is the same as the current page, the
        css class "active" will be added to the <li> tag
        (i.e. <li class="active">...</li>).
    """
    try:
        args = token.split_contents()

        if len(args) < 2:
            raise template.TemplateSyntaxError(
                "%r tag requires at least 2 arguments" % token.contents.split()[0])

        # required arguments
        tag_name = strip_quotes(args.pop(0))
        view = strip_quotes(args.pop(0))
        args = [template.Variable(arg) for arg in args]

        nodelist = parser.parse(('endnavlink',))
        parser.delete_first_token()

        return NavigationLink(nodelist, view, args)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument"
                                           % (tokens.contents.split()[0]))

class NavigationLink(template.Node):

    def __init__(self, nodelist, view, args):
        self.nodelist = nodelist
        self.view = view
        self.args = args

    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        url = reverse(self.view, args=args)
        return '<li class="%(active)s"><a href="%(url)s">%(content)s</a></li>' % {
            'url': url,
            'active': css_active(context, url),
            'content': self.nodelist.render(context),
        }
