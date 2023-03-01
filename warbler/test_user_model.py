"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

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
        
        user1 = User.signup("test1", "test1@test1.com", "password", None)
        uid1 = 11
        user1.id = uid1
        
        user2 = User.signup("test2", "test2@test2.com", "password", None)
        uid2 = 22
        user2.id = uid2
        
        db.session.commit()
        
        user1 = User.query.get(uid1)
        user2 = User.query.get(uid2)
        
        self.u1 = user1
        self.uid1 = uid1

        self.u2 = user2
        self.uid2 = uid2

        
        self.client = app.test_client()
        
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(user.messages), 0)
        self.assertEqual(len(user.followers), 0)
        
        
    def test_user_follows(self):
        self.user1.following.append(self.user2)
        db.session.commit()
        
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user1.following), 1)
        
        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)
    
    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.comit()
        
        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))
        
    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))
        
        
    def test_create_user(self):
        user_test = User.signup("testcreate", "testcreate@test.com", "password", None)
        userid = 7777
        user_test.id = userid
        db.session.commit()
        
        user_test = User.query.get(userid)
        self.assertIsNone(user_test)
        self.assertEqual(user_test.username, "testcreate")
        self.assertEqual(user_test.email, "testcreate@test.com")
        self.assertNotEqual(user_test.password, "password")
        self.assertTrue(user_test.password.startswith("$2b$"))
        
    def test_bad_username_signup(self):
        invalid = User.signup(None, "testcreate@test.com", "password", None)
        userid = 1111111
        invalid.id = userid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
    def test_bad_email_signup(self):
        invalid = User.signup("testcreate", None, "password", None)
        userid = 123789
        invalid.id = userid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testcreate", "testcreate@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)


    def test_valid_authentication(self):
        user = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.uid1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))