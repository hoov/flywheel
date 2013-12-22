""" Tests for fields """
import json

from . import BaseSystemTest
from flywheel import (Field, Model, NUMBER, BINARY, STRING_SET, NUMBER_SET,
                      BINARY_SET, GlobalIndex)


class Widget(Model):

    """ Model for testing default field values """
    __metadata__ = {
        'global_indexes': [
            GlobalIndex('gindex', 'string2', 'num'),
        ],
    }
    string = Field(hash_key=True)
    string2 = Field()
    num = Field(data_type=NUMBER)
    binary = Field(data_type=BINARY, coerce=True)
    str_set = Field(data_type=STRING_SET)
    num_set = Field(data_type=NUMBER_SET)
    bin_set = Field(data_type=BINARY_SET)
    data = Field(data_type=dict)
    wobbles = Field(data_type=bool)

    def __init__(self, **kwargs):
        self.string2 = 'abc'
        for key, val in kwargs.iteritems():
            setattr(self, key, val)


class TestFields(BaseSystemTest):

    """ Tests for default values """
    models = [Widget]

    def test_field_default(self):
        """ If fields are not set, they default to a reasonable value """
        w = Widget()
        self.assertIsNone(w.string)
        self.assertIsNone(w.binary)
        self.assertEquals(w.num, 0)
        self.assertEquals(w.str_set, set())
        self.assertEquals(w.num_set, set())
        self.assertEquals(w.bin_set, set())
        self.assertEquals(w.data, {})
        self.assertEquals(w.wobbles, False)

    def test_set_updates(self):
        """ Sets track changes and update during sync() """
        w = Widget(string='a')
        self.engine.save(w)
        w.str_set.add('hi')
        w.sync()
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(w.str_set, stored_widget.str_set)

    def test_set_updates_fetch(self):
        """ Items retrieved from db have sets that track changes """
        w = Widget(string='a', str_set=set(['hi']))
        self.engine.save(w)
        w = self.engine.scan(Widget).all()[0]
        w.str_set.add('foo')
        w.sync()
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(w.str_set, stored_widget.str_set)

    def test_set_updates_replace(self):
        """ Replaced sets also track changes for updates """
        w = Widget(string='a')
        w.str_set = set(['hi'])
        self.engine.save(w)
        w.str_set.add('foo')
        w.sync()
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(w.str_set, stored_widget.str_set)

    def test_dict_updates(self):
        """ Dicts track changes and update during sync() """
        w = Widget(string='a')
        self.engine.save(w)
        w.data['foo'] = 'bar'
        w.sync()
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(w.data, stored_widget.data)

    def test_store_bool(self):
        """ Dicts track changes and update during sync() """
        w = Widget(string='a', wobbles=True)
        self.engine.save(w)
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertTrue(stored_widget.wobbles is True)

    def test_store_extra_number(self):
        """ Extra number fields are stored as numbers """
        w = Widget(string='a', foobar=5)
        self.engine.save(w)

        table = Widget.meta_.ddb_table(self.dynamo)
        result = list(table.scan())[0]
        self.assertEquals(result['foobar'], 5)
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(stored_widget.foobar, 5)

    def test_store_extra_string(self):
        """ Extra string fields are stored as json strings """
        w = Widget(string='a', foobar='hi')
        self.engine.save(w)

        table = Widget.meta_.ddb_table(self.dynamo)
        result = list(table.scan())[0]
        self.assertEquals(result['foobar'], json.dumps('hi'))
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(stored_widget.foobar, 'hi')

    def test_store_extra_set(self):
        """ Extra set fields are stored as sets """
        foobar = set(['hi'])
        w = Widget(string='a', foobar=foobar)
        self.engine.save(w)

        table = Widget.meta_.ddb_table(self.dynamo)
        result = list(table.scan())[0]
        self.assertEquals(result['foobar'], foobar)
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(stored_widget.foobar, foobar)

    def test_store_extra_dict(self):
        """ Extra dict fields are stored as json strings """
        foobar = {'foo': 'bar'}
        w = Widget(string='a', foobar=foobar)
        self.engine.save(w)

        table = Widget.meta_.ddb_table(self.dynamo)
        result = list(table.scan())[0]
        self.assertEquals(result['foobar'], json.dumps(foobar))
        stored_widget = self.engine.scan(Widget).all()[0]
        self.assertEquals(stored_widget.foobar, foobar)