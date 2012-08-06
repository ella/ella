from django.db import models
from django.test import TestCase

from nose import tools

from ella.core.app_data import AppDataContainer, \
    NamespaceRegistry, AppDataField, NamespaceConflict, NamespaceMissing

app_registry = NamespaceRegistry(default_class=AppDataContainer)

class DummyAppDataClass(models.Model):
    app_data = AppDataField(default='{}', editable=False, app_registry=app_registry)


class DummyAppDataContainer(AppDataContainer):
    pass


class DummyAppDataContainer2(AppDataContainer):
    pass


class TestAppData(TestCase):
    def tearDown(self):
        super(TestAppData, self).tearDown()
        app_registry._reset()

    @tools.raises(NamespaceConflict)
    def test_namespace_can_only_be_registered_once(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.register('dummy', DummyAppDataContainer2)

    @tools.raises(NamespaceMissing)
    def test_unregistered_namespace_cannot_be_unregistered(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.unregister('dummy')
        app_registry.unregister('dummy')

    def test_get_app_data_returns_registered_class_instance(self):
        app_registry.register('dummy', DummyAppDataContainer)
        inst = DummyAppDataClass()
        tools.assert_true(isinstance(inst.app_data.get('dummy', {}), DummyAppDataContainer))

    def test_get_app_data_returns_default_class_if_not_registered(self):
        inst = DummyAppDataClass()
        tools.assert_true(isinstance(inst.app_data.get('dummy', {}), AppDataContainer))

    def test_app_data_container_behaves_like_dict(self):
        inst = DummyAppDataClass()
        data = inst.app_data.get('dummy', {})
        data['foo'] = 'bar'
        tools.assert_equals(data['foo'], 'bar')
        tools.assert_equals(data.keys(), ['foo'])
        tools.assert_equals(data.values(), ['bar'])
