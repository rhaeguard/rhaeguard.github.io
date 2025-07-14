import os
import subprocess
import glob
import pathlib
import re
from datetime import datetime
import shutil
import json
# local code
from templating_engine import render_template
# external dependencies
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.token import STANDARD_TYPES
from PIL import Image

class NewEngineFormatter(HtmlFormatter):
    name = 'NEF'
    
    def __init__(self, **options):
        HtmlFormatter.__init__(self, **options)

    def format(self, tokensource, outfile):
        """
        overriding the same function from the parent class 
        """
        outfile.write('<div class="highlight"><pre>')
        for token_type, value in tokensource:
            tag_name = STANDARD_TYPES[token_type]
            if tag_name == "w" and value == " ":
                outfile.write("&nbsp;")
                continue
            tag_name = f"x{tag_name}"

            value = value.replace("&", "&amp;")
            value = value.replace("<", "&lt;")
            value = value.replace(">", "&gt;")
            value = value.replace('"', "&quot;")
            
            line = f"<{tag_name}>{value}</{tag_name}>"
            outfile.write(line)
        outfile.write('</pre></div>')

    def get_token_style_defs(self, arg=None):
        """
        overriding the same function from the parent class
        """
        prefix = self.get_css_prefix(arg)

        styles = [
            (level, ttype, cls, style)
            for cls, (style, ttype, level) in self.class2style.items()
            if cls and style
        ]
        styles.sort()

        lines = [
            f'{prefix(cls)} {{ {style} }}'
            for (level, ttype, cls, style) in styles
        ]

        return lines

MARKDOWN = markdown.Markdown(extensions=["fenced_code", "sane_lists", "toc"])
PYGMENTS_HTML_FORMATTER = NewEngineFormatter(style="monokai")
CODE_EXTRACTION_REGEX = (
    r"<pre><code class=\"language-([a-z]+)\">((.|\n)+?)<\/code><\/pre>"
)

BUILD_DIR_PATH = pathlib.Path("./build")

with open("./templates/html_template.html") as html_file:
    HTML_TEMPLATE = html_file.read().strip()

with open("./templates/single_post.html") as html_file:
    SINGLE_POST_TEMPLATE = html_file.read().strip()

with open("./templates/index.html") as html_file:
    INDEX_PAGE_TEMPLATE = html_file.read().strip()

with open("data.json", encoding="utf-8") as df:
    CONFIG_DATA = json.load(df)

if not BUILD_DIR_PATH.exists():
    os.makedirs(BUILD_DIR_PATH, exist_ok=True)

def syntax_highlight_code(match):
    lang = match.group(1)
    code = match.group(2)

    code = code.replace("&amp;", "&")
    code = code.replace("&lt;", "<")
    code = code.replace("&gt;", ">")
    code = code.replace("&quot;", '"')

    lexer = get_lexer_by_name(lang, stripall=True)
    return highlight(code, lexer, PYGMENTS_HTML_FORMATTER)

def handle_css():
    # handle CSS
    with open("./css/main.css") as scss_file, open(BUILD_DIR_PATH.joinpath("main.css"), "w+") as main_css:
        raw_css = scss_file.read().strip()

        syntax_highligher_styling: str = PYGMENTS_HTML_FORMATTER.get_style_defs()

        for tag_name in STANDARD_TYPES.values():
            find = f".{tag_name} {{"
            replace = f"x{tag_name} {{"
            syntax_highligher_styling = syntax_highligher_styling.replace(find, replace)

        syntax_highligher_styling = f"""
        .highlight {{
            {syntax_highligher_styling}
        }}
        """

        raw_css += syntax_highligher_styling

        compiled_css = raw_css.replace("\n", "")

        main_css.write(compiled_css)
        main_css.flush()


def handle_static_assets():
    # move the static assets
    for file in glob.glob("./assets/*"):
        filename = pathlib.Path(file).name
        if filename == "favicon.png":
            img = Image.open(file)
            img.save(BUILD_DIR_PATH.joinpath("favicon.ico"), format='ICO', optimize=True)
        elif filename.endswith(".png"):
            img = Image.open(file)
            img = img.convert("RGB")
            new_filename = filename.replace(".png", ".jpeg")
            img.save(BUILD_DIR_PATH.joinpath(new_filename), optimize=True)
        else:
            # copy everything else as-is
            shutil.copy2(file, BUILD_DIR_PATH.joinpath(filename))

def prepare_metadata(post_metadata = None):
    meta = {}
    for category, keys in CONFIG_DATA["global_metadata"].items():
        for key, value in keys.items():
            property = f"{category}:{key}"
            content = value
            meta[property] = content

    if post_metadata:
        post_url = f"{CONFIG_DATA['base_url']}/posts/{post_metadata['filename']}/"
        meta["og:type"] = "article"
        meta["og:url"] = post_url
        meta["og:title"] = post_metadata["title"]

        meta["twitter:url"] = post_url
        meta["twitter:title"] = post_metadata["title"]

    return meta


def get_git_last_modified_date(file_path):
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=iso-strict', '--', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr}")
        return None

def handle_posts():
    posts_metadata = []
    # build the files
    for markdown_file in glob.glob("./posts/*.md"):
        filename = pathlib.Path(markdown_file).name[:-3]
        os.makedirs(BUILD_DIR_PATH.joinpath("posts", filename), exist_ok=True)
        with \
            open(markdown_file, encoding="utf-8") as f, \
            open(BUILD_DIR_PATH.joinpath("posts", filename, "index.html"), "w+", encoding="utf-8") as o:
            
            out_html = MARKDOWN.convert(f.read())

            out_html = re.sub(CODE_EXTRACTION_REGEX, syntax_highlight_code, out_html, 0, re.MULTILINE)

            metadata_end_ix = out_html.find("-->")
            last_modified_date = get_git_last_modified_date(markdown_file)
            post_metadata = {
                "filename": f"{filename}", 
                "last_modified_date": last_modified_date
            }

            if metadata_end_ix != -1:
                metadata = out_html[4:metadata_end_ix]
                for meta in metadata.splitlines():
                    if not meta.strip():
                        continue

                    key, value = meta.strip().split("=", maxsplit=1)
                    key, value = key.strip(), value.strip()
                    post_metadata[key] = value
                    if key == "date" and last_modified_date is None:
                        post_metadata["last_modified_date"] = value

                posts_metadata.append(post_metadata)

                out_html = out_html[metadata_end_ix + 3 :]
            
            out_html = render_template(SINGLE_POST_TEMPLATE, {
                "content": out_html,
                **post_metadata,
            })

            out_html = render_template(HTML_TEMPLATE, {
                "content": out_html,
                "title": post_metadata["title"],
                "meta_data": prepare_metadata(post_metadata)
            })

            o.write(out_html)
            o.flush()

    return posts_metadata

def construct_index_html(posts_metadata):
    with open(BUILD_DIR_PATH.joinpath("index.html"), "w+", encoding="utf-8") as o:
        print("generation started...")

        posts_metadata.sort(key=lambda p: datetime.strptime(p["date"], "%Y-%m-%dT%H:%M:%S%z"), reverse=True)

        index_html = render_template(INDEX_PAGE_TEMPLATE, {
            "projects": CONFIG_DATA["all_projects"],
            "posts": posts_metadata,
        })

        out_html = render_template(HTML_TEMPLATE, {
            "content": index_html,
            "title": CONFIG_DATA["blog_title"],
            "meta_data": prepare_metadata()
        })

        o.write(out_html)
        o.flush()
        print("generation done")

if __name__ == "__main__":
    handle_css()
    handle_static_assets()
    posts_metadata = handle_posts()
    construct_index_html(posts_metadata)