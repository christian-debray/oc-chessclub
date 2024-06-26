from app.commands.commands_abc import CommandManagerInterface
from app.views.views_abc import AbstractView
from yattag import Doc, indent
from abc import abstractmethod


class HTMLBaseView(AbstractView):
    """Base class of views producing HTML documents.
    Provides a document() method to nest some content in a standalone HTML5 document.
    """
    def __init__(self, cmd_manager: CommandManagerInterface, standalone: bool = False):
        super().__init__(cmd_manager)
        self.standalone = standalone
        self.title = None
        self.encoding = "utf8"
        self.lang = "en"
        self.doctype: str = "<!DOCTYPE html>"
        self.stylesheets_links: list[str] = []

    @abstractmethod
    def render(self):
        pass

    def document(self, content: str = "", pretty_print: bool = True) -> str:
        """Renders the full document and returns the HTML code as a string
        """
        doc, tag, text, line = Doc().ttl()
        if self.doctype:
            doc.asis(self.doctype)
        with tag("html"):
            if self.lang:
                doc.attr(lang=self.lang)
            if self.encoding:
                doc.stag("meta", charset=self.encoding)
            if self.title:
                line("title", self.title)
            for css_link in self.stylesheets_links:
                doc.stag("link", rel="stylesheet", href=css_link)
            with tag("body"):
                doc.asis(content)
        if pretty_print:
            return indent(doc.getvalue())
        else:
            return doc.getvalue()


if __name__ == "__main__":
    testdoc = HTMLBaseView(None)
    testdoc.title = "test title"
    testdoc.stylesheets_links = ["toto.css", "css/foo/bar.css", "https://www.no-css.com/not/found/1234"]
    print(testdoc.document("Hello World"))
