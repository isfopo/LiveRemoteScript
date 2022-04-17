from .LiveRemote import LiveRemote


def create_instance(c_instance):
    ''' Creates and returns Remote Script instance '''
    return LiveRemote(c_instance)
