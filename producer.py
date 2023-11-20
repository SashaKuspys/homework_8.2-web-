import pika

from faker import Faker
from contact_model import Contact

fake = Faker()

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='Sasha_K_exchange', exchange_type='direct')
channel.queue_declare(queue='email_queue', durable=True)
channel.queue_bind(exchange='Sasha_K_exchange', queue='email_queue')


def create_tasks():
    for _ in range(10):  # Генеруємо 10 фейкових контактів
        full_name = fake.name()
        email = fake.email()

        contact = Contact(full_name=full_name, email=email)
        contact.save()

        message_body = str(contact.id)  # Використовуємо ObjectID контакту як повідомлення
        channel.basic_publish(exchange='Sasha_K_exchange', routing_key='email_queue', body=message_body)

    print("Messages sent to the email_queue")

    connection.close()


if __name__ == '__main__':
    create_tasks()
