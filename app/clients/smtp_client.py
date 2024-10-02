# email_utils.py

from aiosmtplib import SMTP
from email.message import EmailMessage
from app.core.config import get_app_settings


class SMTPClient:
    def __init__(self, smtp_user: str, smtp_port: str, smtp_password: str) -> None:
        self._smtp_user = smtp_user
        self._smtp_port = smtp_port
        self._smtp_password = smtp_password

    async def send_verification_email(self, to_email: str, token: str):
        message = EmailMessage()
        message["From"] = self._smtp_user
        message["To"] = to_email
        message["Subject"] = "이메일 인증을 완료해주세요"
        html_content = f"""
        <!DOCTYPE html>
        <html xmlns:th="http://www.thymeleaf.org">

        <body>
        <div style="margin:100px;border: 1px solid lightgray; padding:40px 30px;">
            <h1>[이메일 인증]</h1>
            <div style="width: 100%; border-bottom: 1px solid black;"/>
            <br/>
            <p> 아래 코드를 입력하면 이메일 인증이 완료됩니다.</p>
            <br/>
            <div align="center" style="border:1px solid black; font-family:verdana;">
                <h3 style="color:blue"> 이메일 인증 코드 입니다. </h3>
                <div style="font-size:130%"> {token} </div>
            </div>
            <br/>
        </div>

        </body>
        </html>
        """
        message.set_content(
            f"아래 코드를 사용하여 이메일 인증을 완료해주세요:\n\n{token}"
        )
        message.add_alternative(html_content, subtype="html")

        smtp = SMTP(hostname=self._smtp_user, port=self._smtp_port, start_tls=True)
        try:
            await smtp.connect()
            # await smtp.starttls()
            await smtp.login(self._smtp_user, self._smtp_password)
            await smtp.send_message(message)
        except Exception as e:
            print(f"이메일 전송 중 오류 발생: {e}")
            raise
        finally:
            await smtp.quit()
