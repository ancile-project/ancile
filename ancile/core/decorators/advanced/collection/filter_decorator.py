from ancile.core.decorators import *
import logging

logger = logging.getLogger(__name__)


class FilterDecorator(BaseDecorator):

    def __init__(self, scopes=None, is_collection=False):
        super().__init__(scopes, is_collection)
        self.scopes.append('filter')

    def process_call(self, command):

        return NotImplemented
        # I believe it's already in Collection class

        # logger.debug('Calling Filter Decorator')
        # f = command.params.get("lambda_function", False)
        # collection = command.params.get("collection", False)
        # if not f and collection:
        #     raise AncileException("For filter function")
        # new_collection = Collection()
        # for data_point in collection._data_points:
        #     value = f(data_point)
        #     if value:
        #         data_point._advance_policy('filter_keep')
        #         new_collection._data_points.append(data_point)
        #     else:
        #         data_point._advance_policy('filter_remove')
