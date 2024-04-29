import uuid
import streamlit as st
from .common import check_apptoken_from_apikey, get_global_datadir
from .common import remote_file_to_localfile, translate_document
import os
import time
from dotenv import load_dotenv
from .session import PageSessionState

load_dotenv()



def main():
    st.set_page_config(page_title="文档翻译", page_icon="🌐")
    page_state = PageSessionState("translate_document")
    page_state.initn_attr("latest_target_file", None)
    with st.sidebar:
        st.title("🌐 文档翻译")
        tab1, tab2 = st.tabs(["参数设置", "关于"])
        with tab1:
            apikey_box = st.empty()
            if not page_state.app_uid:
                apikey = st.query_params.get("apikey")
                if not apikey:
                    apikey = apikey_box.text_input("请输入 API Key", type="password")

                if apikey:
                    appuid = check_apptoken_from_apikey(apikey)
                    if appuid:
                        page_state.app_uid = appuid
                        page_state.apikey = apikey
                        # apikey_box.empty()

            if not page_state.app_uid:
                st.error("Auth is invalid")
                st.stop()
            param_box = st.container()

        with tab2:
            st.image(
                os.path.join(os.path.dirname(__file__), "document_translate.png"),
                use_column_width=True,
            )

    start_time = time.time()



    # 用于存储临时文件
    document_tempdir = get_global_datadir("temp_translate")

    language = st.selectbox(
        "目标语言",
        ["zh-CN", "en-US", "fr", "de", "ja", "es", "it", "pt", "ru", "ar", "ko", "hi"],
        index=0,
    )

    uploaded_file = st.file_uploader(
        "上传文档", type=["srt", "txt", "pdf", "pptx", "xlsx", "docx"]
    )

    translate_action = st.button("翻译")


    if uploaded_file and translate_action:
        with st.spinner("正在翻译中..."):
            basename = os.path.basename(uploaded_file.name)
            suffix = os.path.splitext(uploaded_file.name)[-1][1:].lower()
            if suffix in ["srt", "txt"]:
                suffix = "txt"
            temp_file = os.path.join(document_tempdir, f"{uuid.uuid4().hex}.{suffix}")
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getvalue())

            resp = translate_document(temp_file, language)
            if resp:
                result = resp[0]
                target_name = f"target_{basename}"
                remote_file_to_localfile(document_tempdir, target_name, result["target"])
                page_state.latest_target_file = os.path.join(document_tempdir, target_name)
                st.download_button(
                    label=f"下载文档",
                    data=open(page_state.latest_target_file, "rb"),
                    file_name=page_state.latest_target_file,
                )
                st.write(f"Time cast {time.time()-start_time} 秒")
                st.write(result)

    if page_state.latest_target_file:
        param_box.download_button(
            label=f"最近文档下载",
            data=open(page_state.latest_target_file, "rb"),
            file_name=page_state.latest_target_file,
            key="translate_download_latest_file",
        )
