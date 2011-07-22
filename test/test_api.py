import json
from hypernotes import web
from hypernotes import logic

TESTDB = 'hypernotes-test'

class TestApi(object):
    @classmethod
    def setup_class(cls):
        web.app.config['ELASTIC_SEARCH_HOST'] = '127.0.0.1:9200'
        web.app.config['ELASTIC_DB'] = TESTDB
        logic.init_db()
        cls.app = web.app.test_client()
        cls.make_fixtures()

    @classmethod
    def teardown_class(cls):
        conn, db = logic.get_conn()
        # TODO: breaks test at the moment ...
        # conn.delete_index(TESTDB)

    @classmethod
    def make_fixtures(self):
        self.username = u'tester'
        inuser = {
            'id': self.username,
            'fullname': 'The Tester'
            }
        indata = {
            'title': 'My New Note',
            'body': '## Xyz',
            'tags': ['abc', 'efg'],
            'owner': self.username
        }
        self.app.post('/api/v1/user', data=json.dumps(inuser))
        out = self.app.post('/api/v1/note', data=json.dumps(indata))
        self.note_id = json.loads(out.data)['id']
        self.thread_id = 'my-test-thread'
        inthread = {
            'id': self.thread_id,
            'title': 'My Test Thread',
            'description': 'None at the moment',
            'notes': [ self.note_id ],
            'owner': self.username
            }
        self.app.post('/api/v1/thread', data=json.dumps(inthread))

    def test_user(self):
        res = self.app.get('/api/v1/user/%s' % self.username)
        data = json.loads(res.data)
        assert data['_source']['fullname'] == 'The Tester', data

    def test_note(self):
        res = self.app.get('/api/v1/note/%s' % self.note_id)
        assert res.status_code == 200, res.status
        data = json.loads(res.data)
        assert data['_source']['body'] == '## Xyz', data

    def test_thread(self):
        res = self.app.get('/api/v1/thread/%s' % self.thread_id)
        data = json.loads(res.data)
        assert data['_source']['title'] == 'My Test Thread', data
