import os
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Function to copy CSS and JS files from HTML to a destination
def copy_files(html_file_path, dst_dir):
    with open(html_file_path, 'r') as html_file:
        soup = BeautifulSoup(html_file.read(), 'html.parser')
        for tag in soup(['link', 'script']):
            src = tag.get('src') or tag.get('href')
            if src and not src.startswith(('http', 'https', '//')):
                src_path = os.path.join(os.path.dirname(html_file_path), src)
                specific_dst_dir = ''
                if '.js' in src_path:
                    specific_dst_dir = 'js/vendor/porto/'
                if '.css' in src_path:
                    specific_dst_dir = 'css/vendor/porto/'
                if '.png' in src_path or '.jpg' in src_path:
                    specific_dst_dir = 'images/custom/'
                if '.ico' in src_path:
                    specific_dst_dir = 'images/favicons/'

                dst_path = os.path.join(dst_dir, specific_dst_dir, os.path.basename(src_path))
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)

# Function to convert src links in an HTML file
def convert_links(html_file_path, static_dir):
    with open(html_file_path, 'r+') as html_file:
        soup = BeautifulSoup(html_file.read(), 'html.parser')
        for tag in soup(['link', 'script']):
            src = tag.get('src') or tag.get('href')
            if src and not src.startswith(('http', 'https', '//')):
                new_src = urljoin(static_dir, src)

                if '.js' in new_src:
                    specific_dst_dir = 'js/vendor/porto/'
                if '.css' in new_src:
                    specific_dst_dir = 'css/vendor/porto/'
                if '.png' in new_src or '.jpg' in new_src:
                    specific_dst_dir = 'images/custom/'
                if '.ico' in new_src:
                    specific_dst_dir = 'images/favicons/'
                
                if tag.name == 'link':
                    tag['href'] = "{% static '" + "static/" + specific_dst_dir + os.path.basename(src) + "' %}"
                else:
                    tag['src'] = "{% static '" + "static/" +  specific_dst_dir + os.path.basename(src) + "' %}"
        html_file.seek(0)
        html_file.write(str(soup))
        html_file.truncate()

# Usage
html_template_path = ''
django_static_folder = ''
copy_files(html_template_path, django_static_folder)
convert_links(html_template_path, django_static_folder)
