import sys
import re
import subprocess
import os

def ensure_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

ensure_package('streamlit')
ensure_package('youtube_transcript_api')
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url_or_id):
    patterns = [
        r'(?:v=|youtu\.be/|youtube\.com/embed/)([\w-]{11})',
        r'^([\w-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError('有効なYouTube動画のURLまたはIDを入力してください。')


def get_transcript(video_id, preferred_langs=['ja', 'en']):
    for lang in preferred_langs:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=[lang]), lang
        except (TranscriptsDisabled, NoTranscriptFound):
            continue
    raise RuntimeError('日本語・英語いずれの字幕も取得できませんでした。')


def format_transcript(transcript, with_time=True):
    if with_time:
        lines = [f"{round(item['start'],1)}秒：{item['text']}" for item in transcript]
    else:
        lines = [item['text'] for item in transcript]
    return '\n'.join(lines)

# Streamlit UI
def main():
    st.title('YouTube自動字幕 文字起こしツール')
    st.write('YouTubeのURLを入力し、「文字起こし開始」ボタンを押してください。')
    url = st.text_input('YouTube動画のURLまたはIDを入力', '')
    with_time = st.checkbox('時刻付きで表示', value=False)
    if st.button('文字起こし開始'):
        if not url.strip():
            st.warning('URLまたはIDを入力してください。')
            return
        try:
            video_id = extract_video_id(url.strip())
        except ValueError as e:
            st.error(str(e))
            return
        try:
            transcript, lang = get_transcript(video_id)
            st.success(f'取得言語: {"日本語" if lang=="ja" else "英語"}')
        except RuntimeError as e:
            st.error(str(e))
            return
        text = format_transcript(transcript, with_time=with_time)
        st.text_area('文字起こし結果（コピペ用）', text, height=400)

if __name__ == '__main__':
    main() 