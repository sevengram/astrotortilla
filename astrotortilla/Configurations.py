# vim:st=4 sts=4 sw=4 et si

class Configurable(object):
    """Configurable - simple configurable properties

    """
    def __init__(self):
        self.__properties = {}
        self.__propertyList = {}
    
    def __del__(self):
        pass

    @property
    def propertyList(self):
        """dict of properties
        Each property is structured in a tuple:
        handle: (name, validation-func, help, value help, default)
        handle = string, internal name of property
        name = string, human understandable name of property
        validation-func = function(param) or None, new value is accepted is function returns without exceptions
        help = tool-tip for the value
        value help = tool-tip for the value entry
        default = default value (not necessarily current)
        """
        return self.__propertyList

    @propertyList.setter
    def propertyList(self, propList):
        """Set the property list dict to propList.
        Should only be set in c'tor of a class inheriting Configurable.
        """
        if type(propList) == dict and\
                len(propList.values()[0]) == 5:
            self.__propertyList = propList


    def setProperty(self, handle, value):
        """Set property value
        @param handle string, name of property
        @param value preferably string, stored if validation function passes
        """
        if handle in self.__propertyList:
            try:
                self.__propertyList[handle][1](value)
            except:
                raise ValueError("Value does not pass validation function")
            self.__properties[handle] = value
        else:
            raise KeyError("Unknown property: %s"%handle)

    def getProperty(self, handle):
        "@return value of property named `handle`"
        if handle in self.__propertyList:
            return self.__properties.get(handle, self.__propertyList[handle][-1])
        else:
            raise KeyError("Unknown property: %s"%handle)
    
    @property
    def configuration(self):
        "Current configuration values as a dict"
        config = {}
        for key in self.__propertyList:
            config[key] = self.getProperty(key)
        return config
    
    @configuration.setter
    def configuration(self, config):
        "Set all config values as a dict"
        for key,value in config.items():
            try:
                self.setProperty(key,value)
            except Exception, detail:
                print "Setting property `%s` failed: %s"%(key, detail)
