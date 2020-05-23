from .Debug import Debug
from .Stats import Stats
from collections import OrderedDict

class Entity:
    # 0 has higher priority than 1. making 1 the default allows us to bump users to front of line
    DEFAULT_ENTITY_PRIORITY = 1
    @staticmethod
    def _empty_resource_tracking_dict():
        return { 'arrival_time': [], 'start_service_time': [], 'finish_service_time': [], 'request': None }

    def __init__(self, env, attributes = {}):
        """
        resources_requested - keeps track of all of the resources that were requested by this entity (in order of visitation)
        attributes - a list of keys/values that apply to this entity (gender, age, etc...)
        creation_time - when the entity was created (initialized in constructor)
        disposal_time - when the entity was disposed of
        """
        if self.process is None:
             raise NotImplementedError("You must define a function called 'process' in your entity class")
        
        self.attributes = attributes

        # Default priority for non-priority-entities is 0
        priority = Entity.DEFAULT_ENTITY_PRIORITY
        if "priority" in self.attributes:
            priority = self.attributes["priority"]
        elif "priority" in dir(self.__class__):
            priority = self.__class__.priority
        
        self.attributes["priority"] = priority
        self.env = env
        self.creation_time = None
        self.resources_requested = OrderedDict()
        self.disposal_time = None # remember to dispose of entities after finishing processing!
    
    def __str__(self):
        return f"{self.name} created_at: {self.creation_time} attributes: {self.attributes}"
    
    def set_attribute(self, attribute_name, attribute_value):
        """
        Record arbitrary set of attributes about the entity.
        Could include things like gender, age, anything really.
        Resources might use attributes to determine how a particular entity is processed.
        """
        self.attributes[attribute_name] = attribute_value

    def get_total_time(self):
        """
        total time that the entity spent in the system (from creation to disposal)
        only accessible once the entity has been disposed
        """
        if self.is_disposed():
            self._calculate_statistics()
            return self.total_time
        else:
            raise Exception("Can't get total time: Entity has not been disposed")
    
    def get_total_waiting_time(self):
        """
        total time that the entity spent queued waiting for resources
        only accessible wonce the entity has been disposed
        """
        if self.is_disposed():
            self._calculate_statistics()
            return self.waiting_time
        else:
            raise Exception("Can't get total waiting time: Entity has not been disposed")

    def get_waiting_time_for_resource(self, resource):
        """
        time that the entity spent waiting for a particular resource
        """
        return self._calculate_waiting_time_for_resource(resource.name)

    def get_total_processing_time(self):
        """
        total time that the entity spent being processed by resources
        """
        if self.is_disposed():
            self._calculate_statistics()
            return self.processing_time
        else:
            raise Exception("Can't get total processing time: Entity has not been disposed")

    def get_processing_time_for_resource(self, resource):
        """
        time that the entity spent being processed by a particular resource
        """
        return self._calculate_processing_time_for_resource(resource.name)
    
    def wait_for_resource(self, resource, priority_override=None):
        """
        The time that a resource is requested
        should be logged as the "arrival time" for the resource.
        """
        Debug.info(f'{self.name} requesting {resource.name}: {self.env.now}')

        self._add_resource_to_visited(resource)
        self.resources_requested[resource.name]["arrival_time"].append(self.env.now)
        priority = priority_override if priority_override is not None else self.attributes["priority"]
        request = resource.request(priority=priority)
        self.resources_requested[resource.name]['request'] = request
        return request
    
    def process_at_resource(self, resource):
        Debug.info(f'{self.name} started processing at {resource.name} : {self.env.now}')        
        self.resources_requested[resource.name]["start_service_time"].append(self.env.now)
        resource.add_resource_check()
        try: 
            service_time = resource.service_time(self)
        except TypeError:
            # if students do not define a resource function that depends on entity
            # still allow them to call it.
            service_time = resource.service_time()
        except Exception:
            raise Exception(f"Error when calling {resource.name} service time function")
        return self.env.timeout(service_time)

    def release_resource(self, resource):
        request = self.resources_requested[resource.name]['request']
        if request is None:
            Debug.info(f"resource has already been released by {self.name}")
        else:
            Debug.info(f'{self.name} finished at {resource.name}: {self.env.now}')
            self.resources_requested[resource.name]["finish_service_time"].append(self.env.now)
            resource.release(request)
            self.resources_requested[resource.name]['request'] = None

    def dispose(self):
        """
        After an entity is finished being processed, it should be disposed
        """
        self.disposal_time = self.env.now
        Debug.info(f"{self.name} disposed: {self.disposal_time}")
        return self.disposal_time

    def is_disposed(self):
        return self.disposal_time is not None
    
    def did_visit_resource(self, resource_name):
        return resource_name in self.resources_requested
    
    def now(self):
        return self.env.now

    def _calculate_waiting_time_for_resource(self, resource_name):
        if not self.did_visit_resource(resource_name):
            return None
        
        resource_stats = self.resources_requested[resource_name]
        return sum([start_time - arrival_time for start_time, arrival_time in zip(resource_stats["start_service_time"], resource_stats["arrival_time"])])

    def _calculate_processing_time_for_resource(self, resource_name):
        if not self.did_visit_resource(resource_name):
            return None
        
        resource_stats = self.resources_requested[resource_name]
        return sum([finish_time - start_time for finish_time, start_time in zip(resource_stats["finish_service_time"], resource_stats["start_service_time"])])

    def _calculate_statistics(self):
        if not self.is_disposed():
            raise Exception("Entity is not yet disposed. Dispose of this entity before calculating stats")
        waiting_time = 0
        processing_time = 0
        for resource_name, _ in self.resources_requested.items():
            waiting_time += self._calculate_waiting_time_for_resource(resource_name)
            processing_time += self._calculate_processing_time_for_resource(resource_name)

        self.total_time = self.disposal_time - self.creation_time
        self.waiting_time = waiting_time
        self.processing_time = processing_time

    def _add_resource_to_visited(self, resource):
        resource_name = resource.name
        Stats._add_resource(resource)
        if not resource_name in self.resources_requested:
            self.resources_requested[resource_name] = Entity._empty_resource_tracking_dict()
    
    def matches_attributes(self, attributes):
        for k, v in attributes.items():
            if k not in self.attributes or self.attributes[k] != v:
                return False
        return True