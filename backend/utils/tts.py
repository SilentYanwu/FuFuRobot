# backend/utils/tts.py
import edge_tts
from typing import AsyncGenerator

async def generate_audio_stream(text: str, voice: str) -> AsyncGenerator[bytes, None]:
    """
    使用 edge-tts 生成音频流
    :param text: 要朗读的文本
    :param voice: 音色名称
    :return: 音频块流
    """
    try:
        communicate = edge_tts.Communicate(text, voice)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        # 可以返回一个空的生成器或是跑错
        yield b""
