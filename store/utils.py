from django.core.mail import send_mail

from music_store.settings import EMAIL_ADDRESS
from store.models import BankInfo


def send_email_about_order(instance):
    if instance.payment.slug == 'przelew-bankowy':
        bank_info = BankInfo.objects.first()
        email_body = """
        Witaj {username}
        
        Dziękujemy za zakupy w naszym sklepie.
        Prosimy o przesłanie kwoty {price} na numer konta {account}
        Nazwa: {name}
        Adres: {address}
        Tytuł przelewu: {title}
        Zamówienie zostanie wysłane w ciągu 3 dni roboczych od daty otrzymania przelewu.
        
        Pozdrawiamy
        Zespół Music Shop
        """.format(username=instance.user.user, price=str(instance.total_price()), account=bank_info.account,
                   name=bank_info.name, address=bank_info.address, title=instance.code)
        email_title = 'Music Shop - Dziekujemy za zamowienie'
        send_mail(email_title, email_body, EMAIL_ADDRESS, [instance.user.user.email])
