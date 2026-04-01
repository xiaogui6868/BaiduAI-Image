import base64
import urllib
import requests
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox


STUDENT_ID = "202335020537"
STUDENT_NAME = "汤明婷"


API_KEY = "bOhC5kIeul0K1psuvNXBmEZU"
SECRET_KEY = "goYnWWb842iuWYz6MaoldJUM8cBYkBaC"

def get_file_content_as_base64(path, urlencoded=False):
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    try:
        response = requests.post(url, params=params, timeout=10)
        return str(response.json().get("access_token"))
    except:
        return None

def recognize_and_parse_image(image_path):
    try:
        token = get_access_token()
        if not token:
            return "❌ 获取Token失败，请检查网络或API_KEY"

        url = "https://aip.baidubce.com/stream/2.0/image-classify/v1/object_recognition?access_token=" + token
        image_base64 = get_file_content_as_base64(image_path)

        payload = json.dumps({
            "image": image_base64,
            "search_mode": "auto",
            "search_result": False,
            "baike_result": False
        }, ensure_ascii=False)

        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"), timeout=15)
        response.encoding = "utf-8"

        desc_list = []
        for line in response.text.splitlines():
            if line.startswith("data:"):
                json_str = line[5:].strip()
                try:
                    json_data = json.loads(json_str)
                    desc = json_data.get("result", {}).get("description", "")
                    if desc:
                        desc_list.append(desc)
                except:
                    continue

        full_result = "".join(desc_list)
        if full_result:
            return f"✅ 识别成功！\n\n{full_result}"
        else:
            return "⚠️ 未识别到有效物体"

    except Exception as e:
        return f"❌ 识别失败：{str(e)}"

def show_gui():
    root = tk.Tk()
    root.title(f"百度AI图像识别工具 - {STUDENT_NAME}({STUDENT_ID})")
    root.geometry("850x650")
    root.minsize(800, 600)

    # 顶部信息栏（学号 + 姓名）
    info_frame = tk.Frame(root)
    info_frame.pack(pady=5)
    tk.Label(info_frame, text=f"学号：{STUDENT_ID}", font=("微软雅黑", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Label(info_frame, text=f"姓名：{STUDENT_NAME}", font=("微软雅黑", 12, "bold")).pack(side=tk.LEFT, padx=10)

    # 结果显示框
    result_box = scrolledtext.ScrolledText(
        root,
        width=90,
        height=24,
        font=("微软雅黑", 12),
        wrap=tk.WORD,
        relief=tk.GROOVE,
        bd=2
    )
    result_box.pack(pady=(15, 10), padx=20)
    result_box.insert(tk.END, "ℹ️  点击下方按钮选择图片开始识别\n")
    result_box.insert(tk.END, "-" * 70 + "\n")

    # 选择图片按钮
    def select_and_recognize():
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
        )
        if not file_path:
            return

        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, "🔍 正在识别中，请稍候...\n")
        root.update()

        result = recognize_and_parse_image(file_path)
        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, result)

    btn = tk.Button(
        root,
        text="选择图片并识别",
        font=("微软雅黑", 15, "bold"),
        command=select_and_recognize,
        bg="#4CAF50",  
        fg="white",   
        padx=40,
        pady=10,
        relief=tk.RIDGE,
        bd=3
    )
    btn.pack(pady=15)

    root.mainloop()

if __name__ == '__main__':
    show_gui()
