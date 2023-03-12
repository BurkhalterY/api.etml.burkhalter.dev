import sys

from app.data import DEFAULT_MATTERS
from app.models import Matter, User


def init():
    Matter.insert(*DEFAULT_MATTERS).run_sync()
    print("Done!")


def grant():
    emails = sys.argv[1:]
    User.update({User.admin: True}).where(User.email.is_in(emails)).run_sync()
    print("Done: " + ", ".join(emails))


def ungrant():
    emails = sys.argv[1:]
    User.update({User.admin: False}).where(User.email.is_in(emails)).run_sync()
    print("Done: " + ", ".join(emails))
