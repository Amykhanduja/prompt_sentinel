from email import policy
from email.parser import BytesParser


def extract_text(file_path: str):

    with open(file_path, "rb") as file:

        message = BytesParser(policy=policy.default).parse(file)

    text = ""

    if message.is_multipart():

        for part in message.walk():

            if part.get_content_type() == "text/plain":

                text += part.get_content()

    else:

        text = message.get_content()

    return text

