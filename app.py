import streamlit as st
import tempfile, os
import hstegolib  # 直接导入我们上传的本地纯Python文件

st.set_page_config(page_title="HStego 隐写工具", page_icon="🔐")
st.title("🔐 HStego 图像隐写工具")
st.caption("纯 Python 版 S-UNIWARD（只支持 PNG 格式）")

# 使用 S_UNIWARD (纯Python实现)
algo = hstegolib.S_UNIWARD()

tab_embed, tab_extract = st.tabs(["📥 嵌入信息", "📤 提取信息"])

with tab_embed:
    cover = st.file_uploader("上传载体图片（必须是 PNG）", type=["png"])
    secret = st.text_area("要隐藏的秘密消息")
    pwd = st.text_input("设置密码", type="password")
    if st.button("开始嵌入", type="primary", disabled=not (cover and secret and pwd)):
        with st.spinner("正在嵌入..."):
            with tempfile.TemporaryDirectory() as tmp:
                cover_path = os.path.join(tmp, cover.name)
                with open(cover_path,"wb") as f: f.write(cover.getbuffer())
                stego_path = os.path.join(tmp, "stego_" + cover.name)
                secret_path = os.path.join(tmp, "secret.txt")
                with open(secret_path, "w", encoding="utf-8") as f: f.write(secret)
                try:
                    algo.embed(cover_path, secret_path, pwd, stego_path)
                    with open(stego_path,"rb") as f: stego_bytes = f.read()
                    st.success("✅ 嵌入成功！")
                    st.download_button("⬇️ 下载含密图片", stego_bytes, file_name="stego_" + cover.name)
                    st.image(stego_path, caption="含密图片（肉眼难以察觉变化）")
                except Exception as e:
                    st.error(f"❌ 失败：{e}")

with tab_extract:
    stego = st.file_uploader("上传含密图片", type=["png"], key="ext")
    pwd2 = st.text_input("密码", type="password", key="pwd2")
    if st.button("开始提取", disabled=not (stego and pwd2)):
        with st.spinner("正在提取..."):
            with tempfile.TemporaryDirectory() as tmp:
                stego_path = os.path.join(tmp, stego.name)
                with open(stego_path,"wb") as f: f.write(stego.getbuffer())
                out_path = os.path.join(tmp, "out.txt")
                try:
                    algo.extract(stego_path, pwd2, out_path)
                    with open(out_path, "r", encoding="utf-8", errors="replace") as f:
                        st.success("✅ 提取成功！")
                        st.text_area("秘密消息", f.read(), height=200)
                except Exception as e:
                    st.error(f"❌ 失败，请检查密码：{e}")
