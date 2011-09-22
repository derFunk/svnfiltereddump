
from unittest import TestCase
from StringIO import StringIO

from svnfiltereddump import SvnLump, LumpBuilder, ContentTin

class SvnRepositoryMock(object):

    def get_tin_for_file(self, path, rev):
        if path == 'file/in/source/repo_rev17' and rev == 17:
            fh = StringIO('xxxXXX')
            return ContentTin(fh, 3, 'FAKESUM')
        else:
            assert False

    def get_properties_of_path(self, path, rev):
        if path == 'file/in/source/repo_rev17' and rev == 17:
            return { 'a': 'x1', 'b': 'x2' }
        elif path == 'dir/in/source/repo_rev2' and rev == 2:
            return { 'a2': 'y1', 'b2': 'y2' }
        else:   
            assert False

    def get_type_of_path(self, path, rev):
        if path == 'file/in/source/repo_rev17' and rev == 17:
            return 'file'
        elif path == 'dir/in/source/repo_rev2' and rev == 2:
            return 'dir'
        else:
            return None
        
class SvnLumpTests(TestCase):

    def setUp(self):
        repo = SvnRepositoryMock()
        self.builder = LumpBuilder(repo);

    def test_delete_lump(self):
        lump = self.builder.delete_path('a/b/c')

        self.assertEqual(lump.get_header_keys(), [ 'Node-path', 'Node-action' ])
        self.assertEqual(lump.get_header('Node-path'), 'a/b/c')
        self.assertEqual(lump.get_header('Node-action'), 'delete')

    def test_add_file_from_source_repo(self):
        lump = self.builder.add_path_from_source_repository('file/in/source/repo_rev17', 17)
        
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action', 'Text-content-length', 'Text-content-md5' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'file/in/source/repo_rev17')
        self.assertEqual(lump.get_header('Node-kind'), 'file')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.get_header('Text-content-length'), '3')
        self.assertEqual(lump.get_header('Text-content-md5'), 'FAKESUM')
        self.assertEqual(lump.properties, { 'a': 'x1', 'b': 'x2' } )
        fh = StringIO()
        lump.content.empty_to(fh)
        fh.seek(0)
        self.assertEqual(fh.read(), 'xxx')

    def test_add_dir_from_source_repo(self):
        lump = self.builder.add_path_from_source_repository('dir/in/source/repo_rev2/', 2)
        
        self.assertEqual(
            lump.get_header_keys(),
            [ 'Node-path', 'Node-kind', 'Node-action' ]
        )
        self.assertEqual(lump.get_header('Node-path'), 'dir/in/source/repo_rev2')
        self.assertEqual(lump.get_header('Node-kind'), 'dir')
        self.assertEqual(lump.get_header('Node-action'), 'add')
        self.assertEqual(lump.properties, { 'a2': 'y1', 'b2': 'y2' } )
