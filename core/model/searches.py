from typing import List


class Condition:
    EQUALS = 'eq'
    NON_EQUALS = 'neq'
    LESS_THAN = 'lt'
    GREAT_THAN = 'gt'
    LESS_OR_EQUAL_THAN = 'lte'
    GREAT_OR_EQUAL_THAN = 'gte'
    IN = 'in'
    NOT_IN = 'nin'
    CONTAINS = 'contains'
    ICONTAINS = 'icontains'  # case insensitive

    ALL_OPERATORS = (EQUALS, NON_EQUALS, LESS_THAN, LESS_OR_EQUAL_THAN,
                     GREAT_THAN, GREAT_OR_EQUAL_THAN, IN, NOT_IN, CONTAINS, ICONTAINS)

    def __init__(self, field_path, operator, value):
        try:
            assert operator in Condition.ALL_OPERATORS, 'Invalid operator provided'
        except AssertionError as e:
            raise Condition.InvalidOperator(e)
        self.field_path = field_path
        self.operator = operator
        self.value = value

    class InvalidOperator(Exception):
        pass


class Search:
    target_class = None  # AudiovisualRecord, Person, Genre

    """
    (
        # this three will be AND
        (Condition, Condition, Condition),  # OR
        (Confition),  # only one condition
    )

    True if one of all conditions for whatever group of conditions is True.

    results = (Search.Builder.new_search(AudiovisualRecord)
                             .add_condition(Condition('reference', Condition.OPERATOR_EQUALS, 'ONE_REFERENCE'))
                             .add_or()
                             .add_condition(Condition('reference', Condition.OPERATOR_EQUALS, 'ANOTHER'))
                             .search(sort_by='-reference'), paginate=True, page=3)
    """
    def __init__(self, klass):
        self.conditions = [[]]
        self.target_class = klass

    class Builder:
        def __init__(self, klass):
            self._search = Search(klass)

        @staticmethod
        def new_search(klass):
            return Search.Builder(klass)

        def add_condition(self, condition: Condition):
            self._search.conditions[-1].append(condition)
            return self

        def add_conditions(self, conditions: List[Condition]):
            self._search.conditions[-1] = self._search.conditions[-1] + conditions
            return self

        def add_or(self):
            self._search.conditions.append([])
            return self

        def search(self, sort_by=None, paginate=False, page_size=20, page=1):
            from core import services
            """
            NOTE: if paginate is set to True, must result the following structure:
            {
                "current_page": i,
                "total_pages": j,
                "results": [
                    // real results
                ]
            }
            """
            return services.search(self._search, sort_by=sort_by, paginate=paginate, page_size=page_size, page=page)
