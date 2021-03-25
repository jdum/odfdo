#!/usr/bin/env python
"""
Create a new presentation from a previous one by extrating some slides, in a
different order.
"""
import os
import sys

from odfdo import Document

filename = "presentation_base.odp"
presentation_base = Document(filename)
output_filename = "my_extracted_slides.odp"

if __name__ == "__main__":
    # extract = sys.argv[1:]
    extract = " 3 5 2 2"

    extracted = Document("presentation")

    body_base = presentation_base.body
    body_extracted = extracted.body

    # Important, copy styles too:
    extracted.delete_styles()
    extracted.merge_styles_from(presentation_base)

    for i in extract.split():
        try:
            slide_position = int(i) - 1
            slide = body_base.get_draw_page(position=slide_position)
        except:
            continue
        if slide is None:
            continue

        slide = slide.clone

        body_extracted.append(slide)

    if not os.path.exists("test_output"):
        os.mkdir("test_output")

    output = os.path.join("test_output", output_filename)

    extracted.save(target=output, pretty=True)
