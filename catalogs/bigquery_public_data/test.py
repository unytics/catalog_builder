import pandas as pd
import jinja2

template = jinja2.Template('''
<table>
    <name>{{ dataset }}.{{ name }}</name>
    <description>{{ description }}</description>
    <columns>{% for column in columns %}{{ column.name }}{{ ", " if not loop.last else "" }}{% endfor %}</columns>
</table>
''')

df = pd.read_parquet('assets.parquet')
df = df.loc[df['asset_type'] == 'table']
print(df['data'].iloc[0])

df['xml'] = df['data'].map(template.render)

# df['data'].to_json('catalog.json', orient='records')

# from dict2xml import dict2xml
# df['xml'] = '<table>' + df['data'].map(dict2xml) + '</table>'
xml = '\n\n'.join(df['xml'])
with open('catalog.xml', 'w') as f:
    f.write(xml)
# df[['xml']].reset_index().to_xml('catalog.xml', index=False, row_name='table')
# breakpoint()

# df[['data']].reset_index().to_xml('catalog.xml', index=False, row_name='table')
