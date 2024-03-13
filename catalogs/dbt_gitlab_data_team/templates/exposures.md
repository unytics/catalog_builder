# Exposures

Exposures are referenced data-usages. There are listed below:


| Type | Name | Description |
|---|---|---|
{% for exposure in exposures -%}
| **{{ exposure.type }}** | [{{ exposure.name }}]({{ exposure.url }}) | {{ exposure.description }} |
{% endfor %}

