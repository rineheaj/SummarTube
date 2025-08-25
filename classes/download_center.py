import streamlit as st
from datetime import datetime
import pandas as pd
import json
import mimetypes
from typing import Union, Optional




class DownloadCenter:
    def __init__(self, title: str = "📩 Dwonload Center"):
        self.title = title
        self.files: dict[str, tuple[Union[str, bytes], str, str]] = {}

    def add_file(
        self, label: str, content: Union[str, bytes], ext: str, mime: Optional[str] = None
    ) -> None:
        if not mime:
            mime, _ = mimetypes.guess_type(f"file{ext}")
            mime = mime or "application/octet-stream"

        self.files[label] = (content, ext, mime)

    def add_dataframe(self, label: str, df: pd.DataFrame):
        csv_data = df.to_csv(index=False)
        self.add_file(label, csv_data, ".csv", "text/csv")

    def add_json(self, label: str, obj: Union[dict, list]):
        json_data = json.dumps(obj, indent=2)
        self.add_file(label, json_data, ".json", "application/json")

    def add_markdown(self, label: str, md_string: str):
        self.add_file(label, md_string, ".md", "text/markdown")

    def add_text(self, label: str, text_string: str):
        self.add_file(label, text_string, ".txt", "text/plain")

    def add_picture(self, label: str, picture_bytes: bytes, ext: str = "png"):
        self.add_file(label, picture_bytes, ext)

    def render(self):
        st.header(self.title)

        for label, (content, ext, mime) in self.files.items():
            st.subheader(label)
            self._check_me_out(content, mime)

            st.download_button(
                label=f"Download {label}",
                data=content,
                file_name=self._timestamped_filename(label=label, ext=ext),
                mime=mime,
            )

    def _check_me_out(self, content: Union[str, bytes], mime: str):
        if mime.startswith("text/markdown"):
            st.markdown(content)
        elif mime.startswith("text/"):
            st.code(content, language="text")
        elif mime.startswith("image/"):
            st.image(content)
        else:
            st.info(
                "Preview not available for this file type check DownloadCenter class"
            )

    def _timestamped_filename(self, label: str, ext: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{label.replace(' ', '_').lower()}_{timestamp}{ext}"
