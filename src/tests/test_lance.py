import base64
import io
import json

import jinja2 as j2
from markupsafe import Markup
import pandas as pd
from PIL import Image
from sql.lance import ResultSet


def image_to_byte_array(image: Image) -> bytes:
    bytearr = io.BytesIO()
    image.save(bytearr, format=image.format)
    return bytearr.getvalue()


def _is_valid_image(img, img_bytes):
    return img == base64.b64encode(img_bytes).decode("UTF-8")


def test_image_embedded():
    with open("cat.jpg", "rb") as fh:
        img_bytes = image_to_byte_array(Image.open(fh))
    df = pd.DataFrame([{"image": None}, {"image": b""}, {"image": img_bytes}])
    rs = ResultSet(df, "foo")
    json_data = json.loads(rs.to_json())
    for record in json_data:
        img = record["image"]
        assert img is None or _is_valid_image(img, img_bytes)


def test_rendering(tmp_path):
    template = "{{ LANCE_OUTPUT_JSON }}"
    index_html = tmp_path / "index.html"
    with index_html.open("w") as fh:
        fh.write(template)
    data = {"LANCE_OUTPUT_JSON": Markup(json.dumps({"foo": "bar"}))}
    with index_html.open("r") as tpl:
        rendered = j2.Template(tpl.read()).render(**data)
    assert rendered == '{"foo": "bar"}'
