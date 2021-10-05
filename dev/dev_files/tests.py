from django.core.files import File
from django.test import TestCase
from uil.files import settings
from uil.files.utils import get_storage

from .models import CustomSingleFile, SingleFile, TrackedCustomFile, TrackedFile


class FakeStorage:

    _storage = {}

    def open(self, name, mode=None):
        if name in self._storage:
            return self._storage[name]

        raise FileNotFoundError

    def save(self, name, content, max_length=None):
        self._storage[name] = content

    def exists(self, name):
        return name in self._storage

    def delete(self, name):
        if name in self._storage:
            del self._storage[name]

    def num_files(self):
        return len(self._storage.keys())

    def clear(self):
        self._storage = {}


class FileTests(TestCase):
    single_cls = SingleFile
    tracked_cls = TrackedFile

    file_cat = 'dev_files/test_files/cat.png'
    file_dog = 'dev_files/test_files/dog.jpg'

    def setUp(self) -> None:
        settings.STORAGE = 'dev_files.tests.FakeStorage'

    def tearDown(self):
        get_storage().clear()

    def test_fake_storage(self):
        self.assertIsInstance(get_storage(), FakeStorage)

    def test_save_delete_single(self):
        MetadataModel = self.single_cls.required_file.field.related_model

        obj = self.single_cls()
        obj.required_file = File(open(self.file_cat, mode='rb'))
        obj.save()

        self.assertTrue(
            get_storage().exists(obj.required_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )

        obj.delete()

        self.assertFalse(
            get_storage().exists(obj.required_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            0
        )
        self.assertEqual(
            0,
            get_storage().num_files(),
            "Storage is not empty"
        )

    def test_single_multiple_use(self):
        MetadataModel = self.single_cls.required_file.field.related_model
        obj_1 = self.single_cls()
        obj_1.required_file = File(open(self.file_cat, mode='rb'))
        obj_1.save()

        self.assertTrue(
            get_storage().exists(obj_1.required_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )

        obj_2 = self.single_cls()
        obj_2.required_file = obj_1.required_file
        obj_2.save()

        self.assertTrue(
            get_storage().exists(obj_1.required_file.name_on_disk)
        )
        self.assertTrue(
            get_storage().exists(obj_2.required_file.name_on_disk)
        )
        self.assertEqual(
            obj_1.required_file.file_instance,
            obj_2.required_file.file_instance,
            "More than one metadata object was created for the same file"
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1,
            "More than one metadata object was created for the same file"
        )
        self.assertEqual(
            self.single_cls.objects.count(),
            2,
            "Second object was not created"
        )

        obj_1.delete()

        self.assertTrue(
            get_storage().exists(obj_2.required_file.name_on_disk),
            "File was removed from storage before it's time"
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1,
            "File object was probably incorrectly deleted (which also should "
            "have raised an integrity error?)"
        )
        self.assertEqual(
            self.single_cls.objects.count(),
            1,
            "Somehow the object referencing the File was not deleted?"
        )

        obj_2.delete()

        self.assertFalse(
            get_storage().exists(obj_2.required_file.name_on_disk),
            "File was not deleted from storage after all references to it were "
            "deleted"
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            0,
            "File model was not deleted after all references to it were deleted"
        )
        self.assertEqual(
            self.single_cls.objects.count(),
            0,
            "Somehow the object referencing the File was not deleted?"
        )
        self.assertEqual(
            0,
            get_storage().num_files(),
            "Storage is not empty"
        )

    def test_tracked_save_delete(self):
        MetadataModel = self.tracked_cls.files.field.related_model

        obj = self.tracked_cls()
        obj.save()
        obj.files.add(File(open(self.file_cat, mode='rb')))

        self.assertTrue(
            get_storage().exists(obj.files.current_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )

        obj.delete()

        self.assertFalse(
            get_storage().exists(obj.files.current_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            0
        )
        self.assertEqual(
            0,
            get_storage().num_files(),
            "Storage is not empty"
        )

    def test_tracked_multiple_files(self):
        MetadataModel = self.tracked_cls.files.field.related_model

        obj = self.tracked_cls()
        obj.save()
        obj.files.add(File(open(self.file_cat, mode='rb')))
        cat_uuid = obj.files.current_file.uuid
        obj.files.add(File(open(self.file_dog, mode='rb')))
        dog_uuid = obj.files.current_file.uuid

        self.assertNotEqual(cat_uuid, dog_uuid)

        self.assertTrue(
            get_storage().exists(obj.files.current_file.name_on_disk)
        )
        self.assertEqual(
            obj.files.current_file.name,
            self.file_dog
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            2
        )
        self.assertEqual(
            len(list(obj.files.all)),
            2
        )

        obj.files.delete(obj.files.current_file)

        self.assertIsNotNone(
            obj.files.current_file
        )

        self.assertFalse(
            get_storage().exists(dog_uuid)
        )
        self.assertTrue(
            get_storage().exists(obj.files.current_file.name_on_disk)
        )
        self.assertEqual(
            obj.files.current_file.name,
            self.file_cat
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )
        self.assertEqual(
            get_storage().num_files(),
            1
        )
        self.assertEqual(
            len(list(obj.files.all)),
            1
        )

        obj.delete()

        self.assertFalse(
            get_storage().exists(obj.files.current_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            0
        )
        self.assertEqual(
            self.tracked_cls.objects.count(),
            0
        )
        self.assertEqual(
            0,
            get_storage().num_files(),
            "Storage is not empty"
        )

    def test_tracked_delete_all(self):
        MetadataModel = self.tracked_cls.files.field.related_model

        obj = self.tracked_cls()
        obj.save()
        obj.files.add(File(open(self.file_cat, mode='rb')))
        cat_uuid = obj.files.current_file.uuid
        obj.files.add(File(open(self.file_dog, mode='rb')))
        dog_uuid = obj.files.current_file.uuid

        obj.files.delete_all()

        self.assertFalse(
            get_storage().exists(cat_uuid)
        )
        self.assertFalse(
            get_storage().exists(dog_uuid)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            0
        )
        self.assertEqual(
            self.tracked_cls.objects.count(),
            1
        )
        self.assertEqual(
            get_storage().num_files(),
            0
        )

    def test_tracked_auto_delete(self):
        MetadataModel = self.tracked_cls.files.field.related_model

        obj = self.tracked_cls()
        obj.save()
        obj.files.add(File(open(self.file_cat, mode='rb')))
        cat_uuid = obj.files.current_file.uuid
        obj.files.add(File(open(self.file_dog, mode='rb')))
        dog_uuid = obj.files.current_file.uuid

        obj.delete()

        self.assertFalse(
            get_storage().exists(cat_uuid)
        )
        self.assertFalse(
            get_storage().exists(dog_uuid)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            0
        )
        self.assertEqual(
            self.tracked_cls.objects.count(),
            0
        )
        self.assertEqual(
            get_storage().num_files(),
            0
        )

    def test_tracked_set_current(self):
        obj = self.tracked_cls()
        obj.save()
        obj.files.add(File(open(self.file_cat, mode='rb')))
        cat_uuid = obj.files.current_file.uuid
        cat_wrapper = obj.files.current_file
        obj.files.add(File(open(self.file_dog, mode='rb')))
        dog_uuid = obj.files.current_file.uuid

        self.assertEqual(
            self.file_dog,
            obj.files.current_file.name,
        )
        self.assertEqual(
            dog_uuid,
            obj.files.current_file.uuid,
        )
        self.assertEqual(
            2,
            get_storage().num_files(),
        )

        obj.files.set_as_current(cat_wrapper)

        self.assertEqual(
            self.file_cat,
            obj.files.current_file.name,
        )
        self.assertEqual(
            cat_uuid,
            obj.files.current_file.uuid,
        )
        self.assertEqual(
            2,
            get_storage().num_files(),
        )
        self.assertEqual(
            len(list(obj.files.all)),
            2
        )

        obj.delete()

    def test_single_set_from_django_file(self):
        MetadataModel = self.single_cls.required_file.field.related_model
        data = File(open(self.file_cat, mode='rb'))

        obj = self.single_cls()
        obj.required_file = data
        obj.save()

        self.assertTrue(
            get_storage().exists(obj.required_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )
        self.assertEqual(
            self.file_cat,
            obj.required_file.name
        )

        obj.delete()

    def test_single_set_from_tuple(self):
        MetadataModel = self.single_cls.required_file.field.related_model
        data = (File(open(self.file_cat, mode='rb')), None, True)

        obj = self.single_cls()
        obj.required_file = data
        obj.save()

        self.assertTrue(
            get_storage().exists(obj.required_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )
        self.assertEqual(
            self.file_cat,
            obj.required_file.name
        )

        obj.delete()

    def test_single_set_from_metadata_model(self):
        MetadataModel = self.single_cls.required_file.field.related_model

        obj_1 = self.single_cls()
        obj_1.required_file = File(open(self.file_cat, mode='rb'))
        obj_1.save()

        obj_2 = self.single_cls()
        obj_2.required_file = obj_1.required_file.file_instance
        obj_2.save()

        self.assertTrue(
            get_storage().exists(obj_2.required_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )
        self.assertEqual(
            get_storage().num_files(),
            1
        )
        self.assertEqual(
            obj_1.required_file.file_instance,
            obj_2.required_file.file_instance,
        )
        self.assertEqual(
            self.file_cat,
            obj_2.required_file.name
        )

        obj_1.delete()
        obj_2.delete()

    def test_single_set_from_file_wrapper(self):
        MetadataModel = self.single_cls.required_file.field.related_model
        data = (File(open(self.file_cat, mode='rb')), None, True)

        obj_1 = self.single_cls()
        obj_1.required_file = data
        obj_1.save()

        obj_2 = self.single_cls()
        obj_2.required_file = obj_1.required_file
        obj_2.save()

        self.assertTrue(
            get_storage().exists(obj_2.required_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )
        self.assertEqual(
            get_storage().num_files(),
            1
        )
        self.assertEqual(
            obj_1.required_file.file_instance,
            obj_2.required_file.file_instance,
        )
        self.assertEqual(
            self.file_cat,
            obj_2.required_file.name
        )

        obj_1.delete()
        obj_2.delete()

    def test_single_set_from_None(self):
        MetadataModel = self.single_cls.required_file.field.related_model

        obj = self.single_cls()
        obj.required_file = File(open(self.file_cat, mode='rb'))
        obj.nullable_file = File(open(self.file_dog, mode='rb'))
        obj.save()
        nullable_uuid = obj.nullable_file.name_on_disk

        self.assertTrue(
            get_storage().exists(obj.nullable_file.name_on_disk)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            2
        )
        self.assertEqual(
            get_storage().num_files(),
            2
        )
        self.assertEqual(
            self.file_dog,
            obj.nullable_file.name
        )

        obj.nullable_file = None
        obj.save()

        self.assertFalse(
            get_storage().exists(nullable_uuid)
        )
        self.assertEqual(
            MetadataModel.objects.count(),
            1
        )
        self.assertEqual(
            get_storage().num_files(),
            1
        )
        self.assertIsNone(
            obj.nullable_file
        )

        obj.delete()


class CustomFileTests(FileTests):
    single_cls = CustomSingleFile
    tracked_cls = TrackedCustomFile
