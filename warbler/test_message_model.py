import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    
    def setUp(self):
        db.drop_all()
        db.create_all()
        
        self.uid = 88888
        u = User.signup("test", "test@test.com", "password", None)
        u.id = self.uid
        db.session.commit()
        
        self.u = User.query.get(self.uid)
        
        self.client = app.test_client()
        
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self):
        
        m= Message(
            text = "warble",
            user_id = self.uid
        )
        
        db.session.add(m)
        db.session.commit()
        
        self.assertEqual(len(self.u.messages),1)
        self.assertEqual(self.u.messages[0].text, "warble")
        
    def test_message_likes(self):
        message1=Message(
            text = "warble1",
            user_id = self.uid
        )
        message2=Message(
            text = "warble2",
            user_id = self.uid
        )
        
        u = User.signup("test2", "test2@test2.com", "password", None)
        uid = 99999
        u.id = uid
        db.session.add_all([message1, message2, u])
        db.session.commit()
        
        
        like = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(1),1)
        self.assertEqual(like[0].message_id,message1.id)
        
        