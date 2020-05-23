import simpy
import numpy as np

# This class defines methods to be mixed in to Resource and PriorityResource from simpy. 
class ResourceStatsMixin:
    VALID_SAMPLE_FREQUENCIES = [0.01, 0.1, 1]
    DECIMAL_MAP = { # maps sample frequencies to decimals
        .01: 2,
        .1: 1,
        1: 0
    }

    @staticmethod
    def _over_time(env, event_list, sample_frequency):
        if sample_frequency not in ResourceStatsMixin.VALID_SAMPLE_FREQUENCIES:
            raise NotImplementedError(f"You must pick a sample frequency in the list {ResourceStatsMixin.VALID_SAMPLE_FREQUENCIES}")
        decimals = ResourceStatsMixin.DECIMAL_MAP[sample_frequency] 
        rounded_event_list = ResourceStatsMixin._rounded_event_list(event_list, decimals)
        current_size = 0
        event_list_over_time = []
        for i in np.around(np.arange(0, env.now, sample_frequency), decimals):
            if i in rounded_event_list:
                # we found an activity that happened here
                last_queue_check = rounded_event_list[i][-1][0]
                current_size = last_queue_check
            event_list_over_time.append(current_size)
        
        return event_list_over_time
    
    @staticmethod
    def _rounded_event_list(event_list, decimals):
        """
        Necessary for turning the list of events collected that capture utilization and queue size over time
        into a "bucketed" list at rounded time intervals. 
        
        This allows queue/utilization sampling to work for continuous time.
        """
        rounded_event_list = {}
        for time, size, status in event_list:
            rounded_time = np.around(time, decimals)
            if rounded_time in rounded_event_list:
                rounded_event_list[rounded_time].append((size, status))
            else:
                rounded_event_list[rounded_time] = [(size, status)]
        return rounded_event_list
    
    def __init__(self, env, *args, **kwargs):
        super().__init__(env, *args, **kwargs)
        if self.service_time is None:
            raise NotImplementedError("You must define a function called 'service_time' in your Resource class")
        self.queue_size = []
        self.utilization_size = []
        self.env = env
        self.name = self.__class__.__name__

    def request(self, *args, **kwargs):
        req = super().request(*args, **kwargs)
        self.add_resource_check(event='request')
        return req

    def release(self, *args, **kwargs):
        rel = super().release(*args, **kwargs)
        self.utilization_size.append((self.env.now, self.count, 'release'))
        return rel
    
    def queue_size_over_time(self, sample_frequency=1):
        return ResourceStatsMixin._over_time(self.env, self.queue_size, sample_frequency)
    
    def number_being_processed_over_time(self, sample_frequency=1):
        return ResourceStatsMixin._over_time(self.env, self.utilization_size, sample_frequency)
    
    def utilization_over_time(self, sample_frequency=1):
        # iterate through each event, calculate the utilization
        utilization = [(x, np.around(y / float(self.capacity), decimals=2), e) for x, y, e in self.utilization_size]
        return ResourceStatsMixin._over_time(self.env, utilization, sample_frequency)    
    
    def add_resource_check(self, event='start'):
        self.utilization_size.append((self.env.now, self.count, event))
        self.queue_size.append((self.env.now, len(self.queue), event))
    
    def now(self):
        return self.env.now
    
    # private
    def _zeros(self, sample_frequency):
        if sample_frequency not in ResourceStatsMixin.VALID_SAMPLE_FREQUENCIES:
            raise NotImplementedError(f"You must pick a sample frequency in the list {ResourceStatsMixin.VALID_SAMPLE_FREQUENCIES}")
        decimals = ResourceStatsMixin.DECIMAL_MAP[sample_frequency] 
        return [0 for _ in np.around(np.arange(0, self.env.now, sample_frequency), decimals)]
    

# all resources are priority resources
class Resource(ResourceStatsMixin, simpy.PriorityResource):
    pass