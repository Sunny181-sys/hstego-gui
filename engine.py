import hstegolib
import os

class StegoError(Exception):
    pass

class HStegoEngine:
    @staticmethod
    def _algo(path):
        if path.lower().endswith((".jpg", ".jpeg")):
            return hstegolib.J_UNIWARD()
        return hstegolib.S_UNIWARD()

    @staticmethod
    def embed(cover_path, secret_text, password, output_path):
        try:
            tmp_secret = output_path + ".secret.tmp"
            with open(tmp_secret, "w", encoding="utf-8") as f:
                f.write(secret_text)
            algo = HStegoEngine._algo(cover_path)
            algo.embed(cover_path, tmp_secret, password, output_path)
            os.remove(tmp_secret)
            return output_path
        except Exception as e:
            raise StegoError(f"嵌入失败：{e}")

    @staticmethod
    def extract(stego_path, password, output_path):
        try:
            algo = HStegoEngine._algo(stego_path)
            algo.extract(stego_path, password, output_path)
            with open(output_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            raise StegoError(f"提取失败：{e}")