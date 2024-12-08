"""Utility classes dealing with API call and auxiliary abilities.

Todo:
    * Implement ``SummarizerTraditional`` to get better performance.
"""

import uuid
import requests
import hashlib
import time

class Translator:
    """Providing translation ability by calling YOUDAO translate API.

    Example:
        ::

            translator = Translator(APP_KEY, APP_SECRET)
            english_text = translator(chinese_text, src="auto", dst="en")

    Read this link to see all `avaliable languages`_.

    .. _`avaliable languages`:
        https://ai.youdao.com/DOCSIRMA/html/trans/api/wbfy/index.html#section-12

    """

    YOUDAO_URL = "https://openapi.youdao.com/api"
    hash_algo = hashlib.sha256()

    def __init__(self, APP_KEY, APP_SECRET):
        self._APP_KEY = APP_KEY
        self._APP_SECRET = APP_SECRET

    @staticmethod
    def _encrypt(sign_str):
        Translator.hash_algo.update(sign_str.encode("utf-8"))
        return Translator.hash_algo.hexdigest()

    @staticmethod
    def _do_request(data):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return requests.post(Translator.YOUDAO_URL, data=data, headers=headers).json()

    @staticmethod
    def _truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10 : size]

    def __call__(self, text, *, src: str, dst: str) -> str:
        curtime = str(int(time.time()))
        salt = str(uuid.uuid1())
        sign_str = (
            self._APP_KEY
            + Translator._truncate(text)
            + salt
            + curtime
            + self._APP_SECRET
        )
        sign = Translator._encrypt(sign_str)
        data = {
            "from": src,
            "to": dst,
            "signType": "v3",
            "curtime": str(int(time.time())),
            "signStr": sign_str,
            "sign": sign,
            "appKey": self._APP_KEY,
            "q": text,
            "salt": salt,
            "sign": sign,
        }
        response = Translator._do_request(data)
        return response["translation"][0]


class Summarizer:
    """Providing text-summarizing ability"""

    def __init__(self, **kwargs):
        pass

    def __call__(self, english_text: str) -> str:
        raise NotImplementedError()


class SummarizerLLM(Summarizer):
    """Providing text-summarizing ability using GPT4-o"""

    def __init__(self, **kwargs):
        from openai import OpenAI
        self._client = OpenAI(**kwargs)

    def __call__(self, english_text: str) -> str:
        completion = self._client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """
                        You are an experienced prompt engineer specialized in 
                        Stable diffusion. Generate suitable keywords to be
                        used in the prompt for the given article (one line per
                        keyword, no extra spaces or characters):
                    """.strip(),
                },
                {"role": "user", "content": english_text},
            ],
        )

        return completion.choices[0].message.content


class SummarizerTraditional(Summarizer):
    pass


__all__ = [Summarizer, SummarizerLLM, SummarizerTraditional, Translator]
