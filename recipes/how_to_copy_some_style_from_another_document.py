"""Minimal example of copy of a style from another document.
"""

from odfdo import Document, Style

_DOC_SEQUENCE = 310


def main():
    document = Document("text")
    body = document.body
    body.clear()

    # Let's imagine the sample_styles.odt document contains an interesting style.
    #
    # So let's first fetch the style:
    try:
        odfdo_styles = Document("sample_styles.odt")
        highlight = odfdo_styles.get_style("text", display_name="Yellow Highlight")
    except Exception:
        # let's create some *very simple* text style.
        highlight = Style(
            "text", display_name="Yellow Highlight", color="blue", italic=True
        )

    # We made some assumptions here:
    #
    # 'text'              : The family of the style, text styles apply on
    #                       individual characters.
    # ”Yellow Highlight”  : The name of the style as we see it in a desktop
    #                       application.
    # display_name        : Styles have an internal name (“Yellow_20_Highlight”
    #                       in this example) but we gave the display_name
    #                       instead.
    #
    # We hopefully have a style object that we add to our own collection:
    document.insert_style(highlight, automatic=True)


if __name__ == "__main__":
    main()
