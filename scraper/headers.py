from fake_http_header import FakeHttpHeader

def get_random_headers():
    fake_header = FakeHttpHeader()
    return {
        'User-Agent': fake_header.user_agent,
        'Accept-Language': fake_header.accept_language,
        'Accept-Encoding': fake_header.accept_encoding,
        'Accept': fake_header.accept,
        'Referer': fake_header.referer,
    }
