import random

from django.core.mail import send_mail

from MxShop.settings import EMAIL_FROM
from users.models import VerifyCode


def generate_code():
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    for i in range(65, 91):  # A-Z
        code_list.append(chr(i))
    for i in range(97, 123):  # a-z
        code_list.append(chr(i))
    myslice = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice)  # list to string

    return verification_code


def send_code_email(email, send_type='register'):
    code = generate_code()
    email_record = VerifyCode(email=email, code=code, send_type=send_type)

    if send_type == 'register':
        email_title = 'MVSizer注册验证码'
        email_body = 'MVSizer注册验证码为：%s' % code
        # send_mail 四个参数: 邮件的标题， 邮件的正文， 邮件的发送方邮箱地址， 接收方的邮件地址
        send_mail(email_title, email_body, EMAIL_FROM, [email])
        email_record.save()

    return code
