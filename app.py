import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="图像隐写工具", page_icon="🔐")
st.title("🔐 图像隐写工具（纯Python LSB版）")
st.caption("无需编译，云端直接运行，支持PNG格式")

def embed_msg(img, msg):
    # 将文字转为二进制
    bin_data = ''.join(format(ord(c), '08b') for c in msg)
    # 用16位记录长度
    length_bin = format(len(bin_data), '016b')
    full_bin = length_bin + bin_data
    
    pixels = list(img.getdata())
    if len(full_bin) > len(pixels) * 3:
        return None  # 容量超限
    
    new_pixels = []
    for i in range(len(full_bin)):
        r, g, b = pixels[i]
        r = (r & ~1) | int(full_bin[i]) # 修改R通道最低位
        new_pixels.append((r, g, b))
    new_pixels.extend(pixels[len(full_bin):])
    
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)
    return new_img

def extract_msg(img):
    pixels = list(img.getdata())
    bin_data = ''.join(str(p[0] & 1) for p in pixels)
    
    length = int(bin_data[:16], 2)
    if length == 0 or length > len(bin_data):
        return ""
        
    msg_bin = bin_data[16:16+length]
    return ''.join(chr(int(msg_bin[i:i+8], 2)) for i in range(0, len(msg_bin), 8))

tab1, tab2 = st.tabs(["📥 嵌入信息", "📤 提取信息"])

with tab1:
    cover = st.file_uploader("上传载体图片（只能是PNG）", type=["png"])
    secret = st.text_area("要隐藏的秘密消息")
    if st.button("开始嵌入", type="primary", disabled=not (cover and secret)):
        with st.spinner("处理中..."):
            img = Image.open(cover).convert('RGB')
            stego_img = embed_msg(img, secret)
            if stego_img:
                buf = io.BytesIO()
                stego_img.save(buf, format='PNG')
                st.success("✅ 嵌入成功！")
                st.download_button("⬇️ 下载含密图片", buf.getvalue(), file_name="stego.png")
                st.image(stego_img, caption="含密图片（肉眼难以察觉）")
            else:
                st.error("❌ 失败：秘密消息太长，这张图片藏不下！")

with tab2:
    stego = st.file_uploader("上传含密图片（PNG）", type=["png"], key="ext")
    if st.button("开始提取", disabled=not stego):
        with st.spinner("提取中..."):
            img = Image.open(stego).convert('RGB')
            msg = extract_msg(img)
            if msg:
                st.success("✅ 提取成功！")
                st.text_area("秘密消息", msg, height=200)
            else:
                st.error("❌ 提取失败：未发现隐藏信息")
