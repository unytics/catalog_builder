# {{ name | title }}

{% for child in children %}
- [{{ child.path.split('/')[-1].split('.')[0] | replace('_', ' ') | title }}]({{ child.path.split('/')[-1] }})
{% endfor %}