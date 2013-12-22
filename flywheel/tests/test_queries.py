""" Tests for engine queries """

from . import BaseSystemTest
from flywheel import Field, Composite, Model, NUMBER, STRING_SET, GlobalIndex


class User(Model):

    """ Model for testing queries """
    __metadata__ = {
        'global_indexes': [
            GlobalIndex('name-index', 'name', 'score'),
        ],
    }
    id = Field(hash_key=True)
    name = Field(range_key=True)
    score = Field(data_type=NUMBER, index='score-index')
    str_set = Field(data_type=STRING_SET)

    def __init__(self, **kwargs):
        for key, val in kwargs.iteritems():
            setattr(self, key, val)


def score_merge(ts, upvotes):
    """ Merge the ts and upvotes """
    return ts + 1000 * upvotes


class Post(Model):

    """ Model for testing composite queries """
    __metadata__ = {
        'global_indexes': [
            GlobalIndex('name-index', 'username', 'score'),
            GlobalIndex('ts-index', 'username', 'ts'),
        ],
    }
    uid = Composite('type', 'id', hash_key=True)
    type = Field()
    id = Field()
    score = Composite('ts', 'upvotes', range_key=True, data_type=NUMBER,
                      merge=score_merge)
    username = Field()
    ts = Field(data_type=NUMBER)
    upvotes = Field(data_type=NUMBER)

    def __init__(self, **kwargs):
        for key, val in kwargs.iteritems():
            setattr(self, key, val)


class TestQueries(BaseSystemTest):

    """ Tests for table queries """
    models = [User]

    def test_first(self):
        """ Query can retrieve first element of results """
        u = User(id='a', name='Adam')
        self.engine.save(u)
        result = self.engine(User).filter(id='a').first()
        self.assertEquals(result, u)

    def test_first_none(self):
        """ If no results, first() returns None """
        result = self.engine(User).filter(id='a').first()
        self.assertIsNone(result)

    def test_one(self):
        """ Query can retrieve first element of results """
        u = User(id='a', name='Adam')
        self.engine.save(u)
        result = self.engine(User).filter(id='a').one()
        self.assertEquals(result, u)

    def test_one_many(self):
        """ If no results, first() returns None """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])
        with self.assertRaises(ValueError):
            self.engine(User).filter(id='a').one()

    def test_one_none(self):
        """ If no results, one() raises exception """
        with self.assertRaises(ValueError):
            self.engine(User).filter(id='a').one()

    def test_force_hash_key(self):
        """ Queries must specify hash key """
        u = User(id='a', name='Adam')
        self.engine.save(u)
        with self.assertRaises(ValueError):
            self.engine.query(User).all()

    def test_filter_hash_key(self):
        """ Queries can filter by hash key """
        u = User(id='a', name='Adam')
        u2 = User(id='b', name='Billy')
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.id == 'a').all()
        self.assertEquals(results, [u])

    def test_limit(self):
        """ Queries can have a limit """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.id == 'a').limit(1).all()
        self.assertEquals(len(results), 1)

    def test_delete(self):
        """ Queries can selectively delete items """
        u = User(id='a', name='Adam')
        u2 = User(id='b', name='Billy')
        self.engine.save([u, u2])

        count = self.engine.query(User).filter(User.id == 'a').delete()
        self.assertEquals(count, 1)
        results = self.engine.scan(User).all()
        self.assertEquals(results, [u2])

    def test_filter_chain(self):
        """ Queries can chain filters """
        u = User(id='a', name='Adam')
        u2 = User(id='b', name='Billy')
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.id == 'a')\
            .filter(User.name == 'Adam').all()
        self.assertEquals(results, [u])

    def test_filter_and(self):
        """ Queries can and filters together """
        u = User(id='a', name='Adam')
        u2 = User(id='b', name='Billy')
        self.engine.save([u, u2])

        results = self.engine.query(User).filter((User.id == 'a') &
                                                 (User.name == 'Adam')).all()
        self.assertEquals(results, [u])

    def test_filter_lt(self):
        """ Queries can filter lt """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.id == 'a')\
            .filter(User.name < 'Adam').all()
        self.assertEquals(results, [u2])

    def test_filter_lte(self):
        """ Queries can filter lte """
        u = User(id='a', name='Aaron')
        u2 = User(id='a', name='Adam')
        u3 = User(id='a', name='Alison')
        self.engine.save([u, u2, u3])

        results = self.engine.query(User).filter(User.id == 'a')\
            .filter(User.name <= u2.name).all()
        self.assertItemsEqual(results, [u, u2])

    def test_filter_gt(self):
        """ Queries can filter gt """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.id == 'a')\
            .filter(User.name > 'Aaron').all()
        self.assertEquals(results, [u])

    def test_filter_gte(self):
        """ Queries can filter gte """
        u = User(id='a', name='Aaron')
        u2 = User(id='a', name='Adam')
        u3 = User(id='a', name='Alison')
        self.engine.save([u, u2, u3])

        results = self.engine.query(User).filter(User.id == 'a')\
            .filter(User.name >= u2.name).all()
        self.assertItemsEqual(results, [u2, u3])

    def test_filter_beginswith(self):
        """ Queries can filter beginswith """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.id == 'a')\
            .filter(User.name.beginswith_('Ad')).all()
        self.assertEquals(results, [u])

    def test_filter_ne(self):
        """ Queries cannot filter ne """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        with self.assertRaises(ValueError):
            self.engine.query(User).filter(User.id == 'a')\
                .filter(User.name != 'Adam').all()

    def test_filter_in(self):
        """ Queries cannot filter in """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        with self.assertRaises(ValueError):
            self.engine.query(User).filter(User.id == 'a')\
                .filter(User.name.in_(set())).all()

    def test_filter_contains(self):
        """ Queries cannot filter contains """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        with self.assertRaises(ValueError):
            self.engine.query(User).filter(User.id == 'a')\
                .filter(User.str_set.contains_('hi')).all()

    def test_filter_null(self):
        """ Queries cannot filter null """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        with self.assertRaises(ValueError):
            self.engine.query(User).filter(User.id == 'a')\
                .filter(User.name == None).all()  # noqa

    def test_filter_not_null(self):
        """ Queries cannot filter not null """
        u = User(id='a', name='Adam')
        u2 = User(id='a', name='Aaron')
        self.engine.save([u, u2])

        with self.assertRaises(ValueError):
            self.engine.query(User).filter(User.id == 'a')\
                .filter(User.name != None).all()  # noqa

    def test_smart_local_index(self):
        """ Queries auto-select local secondary index """
        u = User(id='a', name='Adam', score=50)
        u2 = User(id='a', name='Aaron', score=100)
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.id == 'a')\
            .filter(User.score > 75).all()
        self.assertEquals(results, [u2])

    def test_smart_global_index(self):
        """ Queries auto-select global secondary index """
        u = User(id='a', name='Adam', score=50)
        u2 = User(id='b', name='Adam', score=100)
        self.engine.save([u, u2])

        results = self.engine.query(User).filter(User.name == 'Adam')\
            .filter(User.score > 75).all()
        self.assertEquals(results, [u2])


class TestCompositeQueries(BaseSystemTest):

    """ Tests for table queries """
    models = [Post]

    def test_composite_query(self):
        """ Can query composite fields """
        p = Post(type='tweet', id='1234')
        self.engine.save(p)

        results = self.engine(Post).filter(uid='tweet:1234').all()
        self.assertEquals(results, [p])

    def test_composite_query_piecewise(self):
        """ Can query composite fields by individual pieces """
        p = Post(type='tweet', id='1234')
        self.engine.save(p)

        results = self.engine(Post).filter(type='tweet', id='1234').all()
        self.assertEquals(results, [p])

    def test_composite_local_index(self):
        """ Auto-select composite local secondary indexes """
        p = Post(type='tweet', id='1234')
        self.engine.save(p)

        results = self.engine(Post).filter(type='tweet', id='1234',
                                           score=0).all()
        self.assertEquals(results, [p])

    def test_composite_local_index_piecewise(self):
        """ Auto-select composite local secondary indexes by pieces """
        p = Post(type='tweet', id='1234')
        self.engine.save(p)

        results = self.engine(Post).filter(type='tweet', id='1234', ts=0,
                                           upvotes=0).all()
        self.assertEquals(results, [p])

    def test_composite_global_index(self):
        """ Auto-select composite global secondary indexes """
        p = Post(type='tweet', id='1234', username='abc')
        self.engine.save(p)

        results = self.engine(Post).filter(username='abc', score=0).all()
        self.assertEquals(results, [p])

    def test_composite_global_index_piecewise(self):
        """ Auto-select composite global secondary indexes by pieces """
        p = Post(type='tweet', id='1234', username='abc')
        self.engine.save(p)

        results = self.engine(Post).filter(username='abc', ts=0,
                                           upvotes=0).all()
        self.assertEquals(results, [p])

    def test_ambiguous_index(self):
        """ Error raised if index name is ambiguous """
        p = Post(type='tweet', id='1234', username='abc')
        self.engine.save(p)

        with self.assertRaises(ValueError):
            self.engine(Post).filter(username='abc').all()

    def test_select_index(self):
        """ Index name can be specified """
        p = Post(type='tweet', id='1234', username='abc')
        self.engine.save(p)

        results = self.engine(Post).filter(username='abc')\
            .index('name-index').all()
        self.assertEquals(results, [p])

    def test_no_index(self):
        """ If no index is found, error is raised """
        p = Post(type='tweet', id='1234')
        self.engine.save(p)

        with self.assertRaises(ValueError):
            self.engine(Post).filter(Post.username == 'a')\
                .filter(Post.upvotes == 4).all()