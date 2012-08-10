from django.db import models
from django.test import TestCase
from django.conf import settings

from nose import tools

from ella.core.app_data import NamespaceRegistry, AppDataField, NamespaceConflict, NamespaceMissing, app_registry as global_app_registry
from ella.articles.models import Article

class AppDataContainer(dict):
    pass

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
        if hasattr(settings, 'APP_DATA_CLASSES'):
            del settings.APP_DATA_CLASSES
        app_registry._reset()
        global_app_registry._reset()

    def test_classes_can_be_overriden_from_settings(self):
        settings.APP_DATA_CLASSES = {
                'global': {'testing': 'test_ella.test_core.test_appdata.DummyAppDataContainer'},
                'core.publishable': {'testing': 'test_ella.test_core.test_appdata.DummyAppDataContainer2'}
            }
        # re-initialize app_registries
        app_registry._reset()
        global_app_registry._reset()

        art = Article()
        art.app_data = {'testing': {'answer': 42}}
        inst = DummyAppDataClass()
        inst.app_data = {'testing': {'answer': 42}}

        tools.assert_true(isinstance(art.app_data['testing'], DummyAppDataContainer2))
        tools.assert_true(isinstance(inst.app_data['testing'], DummyAppDataContainer))

    def test_registered_classes_can_behave_as_attrs(self):
        global_app_registry.register('dummy', DummyAppDataContainer)
        art = Article()
        tools.assert_true(isinstance(art.app_data.dummy, DummyAppDataContainer))

    def test_registered_classes_can_be_set_as_attrs(self):
        global_app_registry.register('dummy', DummyAppDataContainer)
        art = Article()
        art.app_data.dummy = {'answer': 42}
        tools.assert_true(isinstance(art.app_data.dummy, DummyAppDataContainer))
        tools.assert_equals(DummyAppDataContainer({'answer': 42}), art.app_data.dummy)
        tools.assert_equals({'dummy': {'answer': 42}}, art.app_data)

    def test_registered_classes_get_stored_on_access(self):
        global_app_registry.register('dummy', DummyAppDataContainer)
        art = Article()
        art.app_data['dummy']
        tools.assert_equals({'dummy': {}}, art.app_data)

    @tools.raises(NamespaceConflict)
    def test_namespace_can_only_be_registered_once(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.register('dummy', DummyAppDataContainer2)

    @tools.raises(NamespaceMissing)
    def test_unregistered_namespace_cannot_be_unregistered(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.unregister('dummy')
        app_registry.unregister('dummy')

    def test_override_class_for_model_only(self):
        app_registry.register('dummy', DummyAppDataContainer)
        app_registry.register('dummy', DummyAppDataContainer2, model=DummyAppDataClass)
        inst = DummyAppDataClass()
        tools.assert_true(isinstance(inst.app_data.get('dummy', {}), DummyAppDataContainer2))

    def test_get_app_data_returns_registered_class_instance(self):
        app_registry.register('dummy', DummyAppDataContainer)
        inst = DummyAppDataClass()
        tools.assert_true(isinstance(inst.app_data.get('dummy', {}), DummyAppDataContainer))

    def test_existing_values_get_wrapped_in_proper_class(self):
        app_registry.register('dummy', DummyAppDataContainer)
        inst = DummyAppDataClass()
        inst.app_data = {'dummy': {'hullo': 'there'}}
        tools.assert_true(isinstance(inst.app_data['dummy'], DummyAppDataContainer))

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
