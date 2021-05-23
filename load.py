from notionclientwhocandownload import NotionClientWhoCanDownload
import pathlib
import os
client = NotionClientWhoCanDownload(token_v2=os.environ.get('NOTION_V2'))

page = client.get_block("https://www.notion.so/zpix/NSU-DOCS-761a53f14fb048d4af34f68ad49eaaf9")

for child in page.children:
    pathlib.Path('pdf').mkdir(parents=True, exist_ok=True)
    path = f'pdf/{child.title}-{child.id}.pdf'
    client.download_block(child.id, path, export_type='pdf')