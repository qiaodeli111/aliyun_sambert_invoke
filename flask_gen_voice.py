import os
import wave
import dashscope
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts import ResultCallback, SpeechSynthesizer, SpeechSynthesisResult
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

# 配置文件路径
config_file = 'config.txt'

# 更新配置（API 密钥和模型名称）
def save_config(api_key, model_name):
    with open(config_file, 'w') as file:
        file.write(f"{api_key}\n{model_name}")

# 读取配置
def get_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            lines = file.read().strip().split('\n')
            if len(lines) == 2:
                return lines[0], lines[1]
            elif len(lines) == 1:
                return lines[0], None
    return None, None

class Callback(ResultCallback):
    def __init__(self):
        self.audio_frames = []

    def on_open(self):
        print('Speech synthesizer is opened.')

    def on_complete(self):
        print('Speech synthesizer is completed.')
        self.save_audio('output.wav')

    def on_error(self, response: SpeechSynthesisResponse):
        print('Speech synthesizer failed, response is %s' % (str(response)))

    def on_close(self):
        print('Speech synthesizer is closed.')

    def on_event(self, result: SpeechSynthesisResult):
        audio_frame = result.get_audio_frame()
        if audio_frame is not None:
            self.audio_frames.append(audio_frame)

    def save_audio(self, file_name):
        # 确保 static 目录存在
        if not os.path.exists(app.static_folder):
            os.makedirs(app.static_folder)

        # 构建完整的文件路径
        full_path = os.path.join(app.static_folder, file_name)

        with wave.open(full_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(b''.join(self.audio_frames))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        api_key = request.form.get("api_key")
        model_name = request.form.get("model_name") or 'sambert-zhichu-v1' # 如果模型名称为空，使用默认值
        text = request.form.get("text")
        save_config(api_key, model_name)  # 保存 API 密钥和模型名称
        dashscope.api_key = api_key

        callback = Callback()
        SpeechSynthesizer.call(model=model_name,
                               text=text,
                               sample_rate=48000,
                               callback=callback,
                               word_timestamp_enabled=True,
                               phoneme_timestamp_enabled=True)

        return 'static/output.wav'  # 返回音频文件的路径
    else:
        api_key, model_name = get_config()  # 读取 API 密钥和模型名称
        return render_template("index.html", api_key=api_key, model_name=model_name)

    return render_template("index.html")

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(port=20000, debug=True)
