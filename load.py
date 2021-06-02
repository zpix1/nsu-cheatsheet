from notionclientwhocandownload import NotionClientWhoCanDownload
import pathlib
import os
from urllib.parse import quote

client = NotionClientWhoCanDownload(token_v2=os.environ.get('NOTION_V2'))

CONTENT_BRANCH_PREFIX = 'https://raw.githubusercontent.com/zpix1/nsu-cheatsheet/content/'

page = client.get_block('https://www.notion.so/zpix/NSU-PUBLIC-033de7a6eece42c8af52bcf63ad540e5')

def page_children(page):
    result = []
    if page.type == 'collection_view_page':
        for c in page.collection.get_rows():
            if c.get_property('status') == 'Completed':
                result.append(c)
    else:
        return [child for child in page.children if child.type in ('page', 'collection_view_page') ]
    return result[:2]

def load_page_tree(page, path):
    print(f'Loading {page.title} to {path}')
    if len(page_children(page)) != 0:
        print(f'Found {len(page_children(page))} children, creating subdir + README')
        subdir = path / page.title
        subdir.mkdir(parents=True, exist_ok=True)

        page_list = f'### {page.title}\n'

        for i, child in enumerate(page_children(page)):
            print(f'Child {child.title}')
            child_path = subdir / f'{child.title}.pdf'
            page_list += f'{i+1}. [{child.title}]({CONTENT_BRANCH_PREFIX}{quote(str(child_path))})\n'
            load_page_tree(child, subdir)
        
        with open(subdir / f'{page.title}.md', 'w') as f:
            f.write(page_list)
    else:
        print(f'No children found, a regular page, exporting')
        export_path = path / f'{page.title}.pdf'
        client.download_block(page.id, export_path, export_type='pdf')

load_page_tree(page, pathlib.Path('./pdf'))

# for child in page.children:
#     print(f'Loading {child.title}')
#     pathlib.Path('pdf').mkdir(parents=True, exist_ok=True)
#     path = f'pdf/{child.title}.pdf'
#     client.download_block(child.id, path, export_type='pdf')