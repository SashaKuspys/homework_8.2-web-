import pika
import sys

from contact_model import Contact


def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='email_queue', durable=True)

    def send_email_stub(contact_id):
        # Функція-заглушка для імітації надсилання електронного листа
        print(f"Sending email to contact with ID: {contact_id}")

        # Зміна статусу контакту на message_sent = True
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.message_sent = True
            contact.save()
        except Contact.DoesNotExist:
            print(f"Contact with ID {contact_id} not found.")

    # Функція для обробки повідомлень з черги
    def callback(ch, method, properties, body):
        contact_id = body.decode('utf-8')
        send_email_stub(contact_id)
        print(f"Received and processed message for contact with ID: {contact_id}")

        # Підтвердження оброблення повідомлення
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Вказуємо, що споживач може обробляти тільки одне повідомлення одночасно
    channel.basic_qos(prefetch_count=1)

    # Вказуємо, що споживач оброблятиме повідомлення послідовно
    channel.basic_consume(queue='email_queue', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)


