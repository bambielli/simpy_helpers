class Stats:
    """
    Tracks both entities and resources so we can query for summary statistics at the end of the simulation.
    This is reset when Source.start() is called
    """
    summary = None
    def __init__(self):
        self.entities = []
        self.resources = {}
        Stats.summary = self
    
    # Entity Stats Methods
    
    @staticmethod
    def get_entities():
        Stats._check_for_instance_or_raise()
        return Stats.summary._get_disposed_entities()
    
    @staticmethod
    def get_total_times(attributes=None):
        Stats._check_for_instance_or_raise()
        filtered_entities = Stats.summary._filter_entities(attributes)
        return [entity.get_total_time() for entity in filtered_entities]

    @staticmethod
    def get_waiting_times(resource=None, attributes=None):
        Stats._check_for_instance_or_raise()
        
        if resource is not None:
            return Stats.summary._get_waiting_times_for_resource(resource, attributes)
        
        filtered_entities = Stats.summary._filter_entities(attributes)
        return [entity.get_total_waiting_time() for entity in filtered_entities]
    
    @staticmethod
    def get_processing_times(resource=None, attributes=None):
        Stats._check_for_instance_or_raise()
        
        if resource is not None:
            return Stats.summary._get_processing_times_for_resource(resource, attributes)
        
        filtered_entities = Stats.summary._filter_entities(attributes)
        return [entity.get_total_processing_time() for entity in filtered_entities]
    
    @staticmethod
    def queue_size_over_time(resource, sample_frequency=1):
        Stats._check_for_instance_or_raise()
        try:
            tracked_resource = Stats.summary.resources[resource.name]
            return tracked_resource.queue_size_over_time(sample_frequency)
        except KeyError:
            # resource wasn't visited, return a list of zeros
            return resource._zeros(sample_frequency)
    
    @staticmethod
    def utilization_over_time(resource, sample_frequency=1):
        Stats._check_for_instance_or_raise()
        try:
            tracked_resource = Stats.summary.resources[resource.name]
            return tracked_resource.utilization_over_time(sample_frequency)
        except KeyError:
            # resource wasn't visited, return a list of zeros
            return resource._zeros(sample_frequency)

    @staticmethod
    def number_being_processed_over_time(resource, sample_frequency=1):
        Stats._check_for_instance_or_raise()
        try:
            tracked_resource = Stats.summary.resources[resource.name]
            return tracked_resource.number_being_processed_over_time(sample_frequency)
        except KeyError:
            # resource wasn't visited, return a list of zeros
            return resource._zeros(sample_frequency)
    
    @staticmethod
    def _add_resource(resource):
        resource_name = resource.name
        if not resource_name in Stats.summary.resources:
            Stats.summary.resources[resource.name] = resource
    
    @staticmethod
    def _add_entity(entity):
        Stats.summary.entities.append(entity)
    
    @staticmethod
    def _check_for_instance_or_raise():
        if Stats.summary is None:
            raise Exception("Run a simulation before querying for statistics")
    
    @staticmethod
    def _filter_entities_on_matched_attributes(entities=[], attributes=None):
        if attributes is not None:
            return [entity for entity in entities if entity.matches_attributes(attributes)]
        return entities
    
    def _filter_entities(self, attributes):
        disposed_entities = Stats.summary._get_disposed_entities()
        return Stats._filter_entities_on_matched_attributes(disposed_entities, attributes)

    def _get_waiting_times_for_resource(self, resource, attributes):
        filtered_entities = self._filter_entities(attributes)
        waiting_times = [entity.get_waiting_time_for_resource(resource) for entity in filtered_entities]
        return [time for time in waiting_times if time is not None]
    
    def _get_processing_times_for_resource(self, resource, attributes):
        filtered_entities = self._filter_entities(attributes)
        processing_times = [entity.get_processing_time_for_resource(resource) for entity in filtered_entities]
        return [time for time in processing_times if time is not None]

    def _get_disposed_entities(self):
        return [entity for entity in Stats.summary.entities if entity.is_disposed()]