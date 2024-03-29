"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database.

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup(
            "test1",
            "test1@test.com",
            "password",
            None
        )

        u2 = User.signup(
            "test2",
            "test2@test.com",
            "password",
            None
        )
        
        db.session.commit()
        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        # res = super().tearDown()
        db.session.rollback()
        # return res

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test_user_repr(self):
        """Does the repr method work as expected?"""

        self.assertEqual(
            self.u1.__repr__(),
            f'<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>'
        )

    def test_is_following(self):
        """ Does is_following successfully detect when user1 is following user2?"""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        """ Does is_following successfully detect when user1 is following user2?"""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_signup_validity(self):
        """ Does User.signup successfully create a new user given valid credentials? """
            
        user1 = User.signup(
            "TestingSignup",
            "TestingUserSignup@gmail.com",
            "password",
            None,
        )

        db.session.commit()

        self.assertTrue(user1 in User.query.all())

    def test_signup_fail(self):
        """ Does User.signup fail to create a new user if 
        any of the validations (e.g. uniqueness, non-nullable fields) fail? """
        user2 = User.signup(
            None,
            "InvalidUser@gmail.com",
            "password",
            None,
        )

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_authen_success(self):
        """ Does User.authenticate successfully return a user """

        test_user = User.authenticate("test1", "password")
        self.assertTrue(test_user)

    def test_authen_user_fail(self):
        """ Does User.authenticate fail when username is invalid """

        test_user = User.authenticate("swaggy", "password")
        self.assertFalse(test_user)

    def test_authen_password_fail(self):
        """ Does User.authenticate fail when password is invalid """

        test_user = User.authenticate("test1", "swaggy")
        self.assertFalse(test_user)
    
