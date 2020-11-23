from .Debug import Debug
from .Stats import Stats

class Source:
    """
    keeps track of entities that have been produced for simluation
    """
    def __init__(self, env, first_creation=None, number=float("Inf")):
        if self.interarrival_time is None:
            raise NotImplementedError("Provide a method named interarrival_time_generator on your Source Class")
        self._interarrival_time_generator_template = self._interarrival_time_generator_factory() 
        self.env = env
        self.first_creation = first_creation
        self.number = number
        self.count = 0
    
    def next_entity(self):
        for time in self._interarrival_time_generator():
            self.count += 1
            if self.count > self.number:
                # we've reached the number we need to source
                # They will finish processing before simulation ends
                break 
            timeout = self.env.timeout(time)
            creation_time = self.env.now + time
            entity = self.build_entity()
            entity.creation_time = creation_time
            entity.name = f"{entity.__class__.__name__} {self.count}"
            entity.attributes["type"] = entity.__class__ # useful for filtering later
            Stats._add_entity(entity)
            yield timeout, entity        
    
    def start(self, debug=False):
        self._configure_debug(debug)
        self._initialize_stats()
        for arrival_time, entity in self.next_entity():
            yield arrival_time # wait for the next entity to appear
            Debug.info(entity)
            p = self.env.process(entity.process())
            p.callbacks.append(self._dispose(entity)) # disposal happens automatically
    
    def get_build_count(self):
        """
        Returns the current build_count. 
        """
        return self.count
    
    def now(self):
        return self.env.now
    
    # private methods
    
    def _initialize_stats(self):
        Stats()
    
    def _configure_debug(self, debug):
        Debug.DEBUG = debug
        if Debug.DEBUG:
            print("Debug is Enabled")
    
    def _interarrival_time_generator(self):
        # if first_creation exists, emit it as the first time, else just use the interarrival_time
        if self.first_creation is not None:
            yield self.first_creation
        for time in self._interarrival_time_generator_template:
            yield time
    
    def _interarrival_time_generator_factory(self):
        while True:
            yield self.interarrival_time()
    
    def _dispose(self, entity):
        """
        This is used to append dispose to the end of the entity.process callback list
        It needs to be a lambda. 
        """
        return lambda _: (entity.dispose())