import streamlit as st
import tempfile, os
from engine import HStegoEngine, StegoError

st.set_page_config(page_title="HStego 隐写工具", page_icon="🔐")
st.title("🔐 HStego 图像隐写工具")
st.caption("UNIWARD + STC | 最难被检测的图像隐写")

tab1, tab2 = st.tabs(["📥 嵌入信息", "📤 提取信息"])

with tab1:
    cover = st.file_uploader("上传载体图片（PNG/JPG）", type=["png","jpg","jpeg"])
    secret = st.text_area("要隐藏的秘密消息")
    pwd = st.text_input("设置密码", type="password")
    if st.button("开始嵌入", type="primary", disabled=not (cover and secret and pwd)):
        with st.spinner("嵌入中，首次运行可能较慢..."):
            with tempfile.TemporaryDirectory() as tmp:
                cover_path = os.path.join(tmp, cover.name)
                with open(cover_path,"wb") as f: f.write(cover.getbuffer())
                stem, ext = os.path.splitext(cover.name)
                stego_path = os.path.join(tmp, f"stego_{stem}{ext}")
                try:
                    HStegoEngine.embed(cover_path, secret, pwd, stego_path)
                    with open(stego_path,"rb") as f: stego_bytes = f.read()
                    st.success("✅ 嵌入成功！")
                    st.download_button("⬇️ 下载含密图片", stego_bytes, file_name=f"stego_{cover.name}")
                    col1,col2 = st.columns(2)
                    col1.image(cover_path, caption="原始图片", use_container_width=True)
                    col2.image(stego_path, caption="含密图片", use_container_width=True)
                except StegoError as e:
                    st.error(f"❌ {e}")

with tab2:
    stego = st.file_uploader("上传含密图片", type=["png","jpg","jpeg"], key="ext")
    pwd2 = st.text_input("密码", type="password", key="pwd2")
    if st.button("开始提取", disabled=not (stego and pwd2)):
        with st.spinner("提取中..."):
            with tempfile.TemporaryDirectory() as tmp:
                stego_path = os.path.join(tmp, stego.name)
                with open(stego_path,"wb") as f: f.write(stego.getbuffer())
                out_path = os.path.join(tmp, "out.txt")
                try:
                    msg = HStegoEngine.extract(stego_path, pwd2, out_path)
                    st.success("✅ 提取成功！")
                    st.text_area("秘密消息", msg, height=200)
                except StegoError as e:
                    st.error(f"❌ {e}")