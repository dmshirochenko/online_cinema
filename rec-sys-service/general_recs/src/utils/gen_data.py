from faker import Faker


def generate_users(n_users):
    fake = Faker()
    for _ in range(n_users):
        passwd = fake.password(length=10)
        yield {
            "username": fake.lexify("User-?????"),
            "email": fake.free_email(),
            "password": passwd,
            "confirm": passwd,
        }
