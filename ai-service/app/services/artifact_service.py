import base64

def encode_image(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
