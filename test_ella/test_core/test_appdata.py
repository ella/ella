from django.db import models
from django.test import TestCase

from nose import tools

from ella.core.models.appdata import AppDataContainer, \
    NamespaceRegistry, AppDataField


class DummyAppDataClass(models.Model):
    app_data = AppDataField(default='{}', editable=False)


class DummyAppDataContainer(AppDataContainer):
    pass


class DummyAppDataContainer2(AppDataContainer):
    pass


class TestAppData(TestCase):
    def setUp(self):
        if DummyAppDataClass.app_data_registry.is_registered('dummy'):
            DummyAppDataClass.app_data_registry.unregister('dummy')

    def test_registering(self):
        DummyAppDataClass.app_data_registry.register('dummy', DummyAppDataContainer)
        tools.assert_true(DummyAppDataClass.app_data_registry.is_registered('dummy'))
        DummyAppDataClass.app_data_registry.unregister('dummy')
        tools.assert_false(DummyAppDataClass.app_data_registry.is_registered('dummy'))

    @tools.raises(NamespaceRegistry.NamespaceConflict)
    def test_namespace_can_only_be_registered_once(self):
        DummyAppDataClass.app_data_registry.register('dummy', DummyAppDataContainer)
        DummyAppDataClass.app_data_registry.register('dummy', DummyAppDataContainer2)

    @tools.raises(NamespaceRegistry.NamespaceMissing)
    def test_unregistered_namespace_cannot_be_unregistered(self):
        DummyAppDataClass.app_data_registry.register('dummy', DummyAppDataContainer)
        DummyAppDataClass.app_data_registry.unregister('dummy')
        DummyAppDataClass.app_data_registry.unregister('dummy')

    def test_get_app_data_returns_registered_class_instance(self):
        DummyAppDataClass.app_data_registry.register('dummy', DummyAppDataContainer)
        inst = DummyAppDataClass()
        tools.assert_true(isinstance(inst.app_data['dummy'], DummyAppDataContainer))

    def test_get_app_data_returns_default_class_if_not_registered(self):
        inst = DummyAppDataClass()
        tools.assert_true(isinstance(inst.app_data['dummy'], AppDataContainer))

    def test_app_data_container_behaves_like_dict(self):
        inst = DummyAppDataClass()
        data = inst.app_data['dummy']
        data['foo'] = 'bar'
        tools.assert_equals(data['foo'], 'bar')
        tools.assert_equals(data.keys(), ['foo'])
        tools.assert_equals(data.values(), ['bar'])
