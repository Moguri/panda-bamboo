import weakref
import importlib


class Component(object):
    __slots__ = [
        '_entity',
        'typeid',
        'synchronize',
        '_is_unique',
        '_import_string',
    ]

    def __init__(self):
        self._is_unique = False
        self.synchronize = False
        self._import_string = self.__class__.__module__ + '.' + self.__class__.__name__

    def __del__(self):
        #print("__del__", self)
        pass

    def cleanup(self):
        pass

    @property
    def entity(self):
        return self._entity()

    @property
    def is_unique(self):
        return self._is_unique

    def serialize(self):
        return {'import_string': self._import_string}


class UniqueComponent(Component):
    __slots__ = []

    def __init__(self):
        super().__init__()
        self._is_unique = True


class Entity(object):
    __slots__ = [
        '_components',
        '_new_components',
        '__weakref__',
        'guid',
        'space',
        'netid',
    ]

    def __init__(self, space):
        self._components = {}
        self._new_components = {}
        self.guid = None
        self.space = space
        self.netid = 0

    def __del__(self):
        for k, v in self._components.items():
            for i in v:
                i.cleanup()
        self._components.clear()

        for k, v in self._new_components.items():
            for i in v:
                i.cleanup()
        self._new_components.clear()
        #print("__del__", self)

    def add_component(self, component):
        typeid = component.typeid

        enforce_unique = component.is_unique
        if not enforce_unique:
            try:
                enforce_unique = bool([i for i in self.get_components(typeid) if i.is_unique])
            except KeyError:
                enforce_unique = False

        if enforce_unique and self.has_component(typeid):
            raise RuntimeError('Entity already has component with typeid of {}'.format(typeid))
        component._entity = weakref.ref(self)

        if typeid in self._new_components:
            self._new_components[typeid].append(component)
        else:
            self._new_components[typeid] = [component]

    def remove_component(self, component):
        if component.typeid in self._components:
            d = self._components
            clist = self._components[component.typeid]
        elif component.typeid in self._new_components:
            d = self._new_components
            clist = self._new_components[component.typeid]
        else:
            raise KeyError('Enity has no component with typeid of {}'.format(component.typeid))

        component.cleanup()
        clist.remove(component)
        if not clist:
            del d[component.typeid]

    def get_component(self, typeid):
        if len(self.get_components(typeid)) > 1:
            raise RuntimeError('Entity has more than one component with typeid of {}'.format(typeid))

        return self.get_components(typeid)[0]

    def get_components(self, typeid):
        if typeid in self._components:
            return self._components[typeid]
        elif typeid in self._new_components:
            return self._new_components[typeid]
        else:
            raise KeyError('Enity has no component with typeid of {}'.format(typeid))

    def has_component(self, typeid):
        return typeid in self._components or typeid in self._new_components

    def serialize(self):
        d = {}
        for typeid, clist in self._components.items():
            d[typeid] = []
            for component in clist:
                if component.synchronize:
                    d[typeid].append(component.serialize())
            if not d[typeid]:
                del d[typeid]

        return d

    def update(self, netid, d):
        self.netid = netid
        #print(self.netid, d)
        for typeid, clist in d.items():
            for i, cdata in enumerate(clist):
                mod_parts = cdata['import_string'].split('.')
                cmod = '.'.join(mod_parts[:-1])
                cclass = mod_parts[-1]

                try:
                    component = self.get_components(typeid)[i]
                except (IndexError, KeyError):
                    mod = importlib.import_module(cmod)
                    component = getattr(mod, cclass)()
                    self.add_component(component)

                component.update(cdata)


class System(object):
    __slots__ = [
        'component_types',
    ]

    def init_components(self, dt, entities):
        pass

    def update(self, dt, entities):
        pass


class DuplicateSystemException(Exception):
    pass


class ECSManager(object):
    def __init__(self):
        self.entities = []
        self.systems = {}
        self.next_entity_guid = 0
        self.space = Entity(None)
        self.removed_entities = set()

    def create_entity(self):
        # TODO allow for multiple spaces
        if self.space is None:
            raise RuntimeError("ECSManager.space is None")
        entity = Entity(self.space)
        self._add_entity(entity)

        return entity

    def _add_entity(self, entity):
        entity.guid = self.next_entity_guid
        self.next_entity_guid += 1
        self.entities.append(entity)

    def remove_entity(self, entity):
        if entity.netid != 0:
            self.removed_entities.add(entity.netid)
        self.entities.remove(entity)

    def add_system(self, system):
        name = system.__class__.__name__
        if name in self.systems:
            raise DuplicateSystemException("{} has already been added.".format(name))
        self.systems[name] = system

    def has_system(self, system_str):
        return system_str in self.systems

    def get_system(self, system_str):
        if system_str not in self.systems:
            raise KeyError('No system found with the name of {}'.format(system_str))
        return self.systems[system_str]

    def remove_system(self, system_str):
        if system_str not in self.systems:
            raise KeyError('No system found with the name of {}'.format(system_str))
        del self.systems[system_str]

    def remove_space(self):
        # TODO allow for multiple spaces
        for entity in self.entities[:]:
            if entity.space == self.space:
                self.entities.remove(entity)

        self.space = None

    def _get_components_by_type(self, component_list, component_types):
        components = {k: [] for k in component_types}
        for entity in self.entities:
            for typeid in component_types:
                components[typeid] += getattr(entity, component_list).get(typeid, [])

        return components

    def update(self, dt):
        entities = self.entities[:]

        for system in self.systems.values():
            system.init_components(dt, self._get_components_by_type('_new_components', system.component_types))

        for entity in entities:
            for typeid, clist in entity._new_components.items():
                if typeid in entity._components:
                    entity._components[typeid].extend(clist)
                else:
                    entity._components[typeid] = clist[:]
            entity._new_components.clear()

        for system in self.systems.values():
            system.update(dt, self._get_components_by_type('_components', system.component_types))

