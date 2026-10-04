import streamlit as st
from PIL import Image
import tempfile, os

# 核心：导入老师的 HStego 纯 Python 基座
try:
    import hstegolib
    HAS_HSTEGO = True
except Exception as e:
    HAS_HSTEGO = False

st.set_page_config(page_title="HStego 隐写工具", page_icon="🔐")
st.title("🔐 图像隐写工具")
st.caption("基于 daniellerch/hstego 基座构建（支持中英文）")

if HAS_HSTEGO:
    st.success("✅ HStego UNIWARD+STC 基座已加载！")
else:
    st.warning("⚠️ 当前环境缺少 HStego 底层 C 扩展，已自动切换至纯 Python 兼容模式")

# 纯 Python LSB 算法（作为容灾备份）
def embed_lsb(img, msg):
    msg_bytes = msg.encode('utf-8')
    bin_data = ''.join(format(b, '08b') for b in msg_bytes)
    full_bin = format(len(bin_data), '016b') + bin_data
    pixels = list(img.getdata())
    if len(full_bin) > len(pixels) * 3:
        return None
    new_pixels = []
    for i in range(len(full_bin)):
        r, g, b = pixels[i]
        new_pixels.append(((r & ~1) | int(full_bin[i]), g, b))
    new_pixels.extend(pixels[len(full_bin):])
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)
    return new_img

def extract_lsb(img):
    pixels = list(img.getdata())
    bin_data = ''.join(str(p[0] & 1) for p in pixels)
    length = int(bin_data[:16], 2)
    if length == 0 or length > len(bin_data):
        return ""
    msg_bin = bin_data[16:16+length]
    byte_list = [int(msg_bin[i:i+8], 2) for i in range(0, len(msg_bin), 8)]
    try:
        return bytes(byte_list).decode('utf-8')
    except:
        return ""

tab1, tab2 = st.tabs(["📥 嵌入信息", "📤 提取信息"])

with tab1:
    cover = st.file_uploader("上传载体图片（只能是PNG）", type=["png"])
    secret = st.text_area("要隐藏的秘密消息（支持中英文）")
    pwd = st.text_input("设置密码", type="password")
    if st.button("开始嵌入", type="primary", disabled=not (cover and secret and pwd)):
        with st.spinner("处理中..."):
            with tempfile.TemporaryDirectory() as tmp:
                cover_path = os.path.join(tmp, cover.name)
                with open(cover_path, "wb") as f: f.write(cover.getbuffer())
                stego_path = os.path.join(tmp, "stego_" + cover.name)
                
                try:
                    if HAS_HSTEGO:
                        # 优先调用老师的 HStego 基座
                        algo = hstegolib.S_UNIWARD()
                        algo.embed(cover_path, secret, pwd, stego_path)
                    else:
                        # 容灾降级：调用纯 Python LSB
                        img = Image.open(cover_path).convert('RGB')
                        stego_img = embed_lsb(img, secret)
                        stego_img.save(stego_path, format='PNG')
                    
                    with open(stego_path, "rb") as f: stego_bytes = f.read()
                    st.success("✅ 嵌入成功！")
                    st.download_button("⬇️ 下载含密图片", stego_bytes, file_name="stego.png")
                    st.image(stego_path, caption="含密图片（肉眼难辨）", use_container_width=True)
                except Exception as e:
                    st.error(f"❌ 嵌入失败：{e}")

with tab2:
    stego = st.file_uploader("上传含密图片（PNG）", type=["png"], key="ext")
    pwd2 = st.text_input("密码", type="password", key="pwd2")
    if st.button("开始提取", disabled=not (stego and pwd2)):
        with st.spinner("提取中..."):
            with tempfile.TemporaryDirectory() as tmp:
                stego_path = os.path.join(tmp, stego.name)
                with open(stego_path, "wb") as f: f.write(stego.getbuffer())
                
                try:
                    if HAS_HSTEGO:
                        algo = hstegolib.S_UNIWARD()
                        algo.extract(stego_path, pwd2, os.path.join(tmp, "out.txt"))
                        with open(os.path.join(tmp, "out.txt"), "r", encoding="utf-8", errors="replace") as f:
                            msg = f.read()
                    else:
                        img = Image.open(stego_path).convert('RGB')
                        msg = extract_lsb(img)
                    
                    if msg:
                        st.success("✅ 提取成功！")
                        st.text_area("秘密消息", msg, height=200)
                    else:
                        st.error("❌ 提取失败：未发现隐藏信息")
                except Exception as e:
                    st.error(f"❌ 提取失败：{e}")
